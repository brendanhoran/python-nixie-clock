# Use Python 3 base image
FROM python:3

# Set the branch/version to use for the ESP-IDF framework
ARG ESP_IDF_VERSION = v4.2

# Update apt and install build time dependences
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y cmake

# Download ESP-IDF framework
RUN git clone -b $ESP_IDF_VERSION --recursive https://github.com/espressif/esp-idf.git

RUN cd esp-idf && git submodule update --init --recursive
RUN cd esp-idf && ./install.sh
# This sed is needed to remove the windows only 'file://' refrence, otherwise pip install fails
# https://github.com/espressif/esp-idf/blob/8e3e65a47b7d9b5dc4f52eb56660a748fda1884e/requirements.txt#L38
RUN sed -i '/^file/d' /esp-idf/requirements.txt
RUN pip3 install -r /esp-idf/requirements.txt
# Save the esptool for use later on, its needed for all steps to flash the ESP32
SAVE ARTIFACT /esp-idf/components/esptool_py/esptool/esptool.py AS LOCAL artifacts/

# Export a bunch of esp-idf settings, needed for buiding
ARG IDF_PATH="/esp-idf"
# Find a better way to export Python path based on version 
ARG IDF_PYTHON_ENV_PATH="/root/.espressif/python_env/idf4.2_py3.9_env"
ARG IDF_TOOLS_EXPORT_CMD="/esp-idf/export.sh"
ARG IDF_TOOLS_INSTALL_CMD="/esp-idf/install.sh"
# Don't yet have a better way to export the xtensa path, since it includes a version like 'esp-2020r3-8.4.0'
ENV PATH="/esp-idf/tools/:/root/.espressif/tools/xtensa-esp32-elf/esp-2020r3-8.4.0/xtensa-esp32-elf/bin/:$PATH"

# Download Micropython
RUN git clone https://github.com/micropython/micropython.git
RUN cd micropython && make -C mpy-cross
RUN cd micropython/ports/esp32 && make submodules

# Copy main.py and modules into Micropython build 
# main.py and the modules directory should be top level of the repo.
COPY main.py /micropython/ports/esp32/
COPY modules/ /micropython/ports/esp32/modules/

firmware:
    RUN cd micropython/ports/esp32 && make
    # Save artifacts from building the ESP32 firmware 
    SAVE ARTIFACT /micropython/ports/esp32/build-GENERIC/bootloader/* AS LOCAL artifacts/
    SAVE ARTIFACT /micropython/ports/esp32/build-GENERIC/partition_table/* AS LOCAL artifacts/
    SAVE ARTIFACT /micropython/ports/esp32/build-GENERIC/micropython.bin AS LOCAL artifacts/

flash:
    LOCALLY
    # Define build arg for the serial port (Dont want this in global scope as it will cause layer rebuilds)
    ARG SERIAL_PORT
    # This assumes your host enviroment is able to run 'esptool.py' nativly 
    # No other way around this yet, as we can not pass '--device' docker style syntax into Earthly 
    RUN artifacts/esptool.py -p $SERIAL_PORT -b 460800 --before default_reset --after hard_reset \
        --chip esp32  write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 \
         artifacts/bootloader.bin 0x8000 artifacts/partition-table.bin 0x10000 artifacts/micropython.bin

erase-flash:
    LOCALLY
    # Define build arg for the serial port (Dont want this in global scope as it will cause layer rebuilds)
    ARG SERIAL_PORT
    RUN artifacts/esptool.py --port $SERIAL_PORT erase_flash
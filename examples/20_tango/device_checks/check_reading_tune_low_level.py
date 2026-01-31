import tango

# Create a DeviceProxy
dev = tango.DeviceProxy("simulator/ringsimulator/ringsimulator")

# Read a single attribute
tmp = dev.read_attribute("Tune_h")
tmp = dev.read_attribute("Tune_v")
print(tmp)

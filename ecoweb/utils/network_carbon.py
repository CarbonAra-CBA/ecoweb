def bytes_to_gb(bytes):
    return bytes / (1024 ** 3)

def bytes_to_mb(bytes):
    return bytes / (1024 ** 2)

def energy(bytes):
    return bytes_to_gb(bytes) * 0.81 * 0.75 + (bytes_to_gb(bytes) * 0.02) * 0.81 * 0.25

def carborn(bytes):
    return energy(bytes) * 442

def annual_energy(bytes, traffic=1):
    return energy(bytes) * traffic * 12

def annual_carborn(bytes, traffic=1):
    return carborn(bytes) * traffic * 12

def all_energy(part_e):
    return part_e / 0.52

def all_carborn(part_c):
    return part_c / 0.52

def byte_to_all_e(bytes):
    return all_energy(annual_energy(energy(bytes)))

def byte_to_all_c(bytes):
    return all_carborn(annual_carborn(carborn(bytes)))
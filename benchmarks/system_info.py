"""System hardware detection - CPU, GPU, RAM, Motherboard, BIOS, Drivers."""
import platform
import subprocess
import os
import re


def get_cpu_info():
    """Get detailed CPU information."""
    try:
        import wmi
        w = wmi.WMI()
        for proc in w.Win32_Processor():
            return {
                "name": proc.Name.strip(),
                "manufacturer": proc.Manufacturer,
                "cores": proc.NumberOfCores,
                "threads": proc.NumberOfLogicalProcessors,
                "base_clock_ghz": round(proc.MaxClockSpeed / 1000, 2),
                "current_clock_ghz": round(proc.CurrentClockSpeed / 1000, 2),
                "l2_cache_kb": proc.L2CacheSize,
                "l3_cache_kb": proc.L3CacheSize,
                "architecture": proc.Architecture,
                "socket": proc.SocketDesignation,
                "tdp_watts": getattr(proc, "Tdp", None),
            }
    except Exception:
        pass

    return {
        "name": platform.processor() or "Unknown CPU",
        "manufacturer": "Unknown",
        "cores": os.cpu_count() or 1,
        "threads": os.cpu_count() or 1,
        "base_clock_ghz": None,
        "current_clock_ghz": None,
        "l2_cache_kb": None,
        "l3_cache_kb": None,
        "architecture": None,
        "socket": None,
        "tdp_watts": None,
    }


def get_gpu_info():
    """Get GPU information via WMI."""
    try:
        import wmi
        w = wmi.WMI()
        gpus = []
        for gpu in w.Win32_VideoController():
            vram_bytes = gpu.AdapterRAM
            vram_gb = round(vram_bytes / (1024 ** 3), 1) if vram_bytes and vram_bytes > 0 else None
            gpus.append({
                "name": gpu.Name.strip() if gpu.Name else "Unknown",
                "manufacturer": gpu.AdapterCompatibility or "Unknown",
                "vram_gb": vram_gb,
                "driver_version": gpu.DriverVersion or "Unknown",
                "driver_date": gpu.DriverDate or "Unknown",
                "status": gpu.Status,
                "video_mode": gpu.VideoModeDescription or "Unknown",
            })
        return gpus
    except Exception:
        pass

    try:
        gputil_info = []
        from GPUtil import getGPUs
        for gpu in getGPUs():
            gputil_info.append({
                "name": gpu.name,
                "manufacturer": "NVIDIA",
                "vram_gb": round(gpu.memoryTotal / 1024, 1) if gpu.memoryTotal else None,
                "driver_version": "Unknown",
                "driver_date": "Unknown",
                "status": "OK",
                "video_mode": "Unknown",
                "load": gpu.load * 100 if gpu.load else 0,
                "temperature": gpu.temperature if hasattr(gpu, 'temperature') else None,
                "memory_used": round(gpu.memoryUsed / 1024, 1) if gpu.memoryUsed else None,
                "memory_free": round(gpu.memoryFree / 1024, 1) if gpu.memoryFree else None,
            })
        return gputil_info if gputil_info else [{"name": "Unknown GPU", "manufacturer": "Unknown"}]
    except Exception:
        pass

    return [{"name": "Unknown GPU", "manufacturer": "Unknown"}]


def get_ram_info():
    """Get RAM information."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024 ** 3), 1)
        used_gb = round(mem.used / (1024 ** 3), 1)
        available_gb = round(mem.available / (1024 ** 3), 1)
        percent = mem.percent
    except Exception:
        total_gb = used_gb = available_gb = 0
        percent = 0

    # Try to get RAM speed and type from WMI
    speed_mhz = None
    ram_type = "DDR"
    dimms = []
    try:
        import wmi
        w = wmi.WMI()
        for mem in w.Win32_PhysicalMemory():
            speed_mhz = mem.Speed
            cap_gb = round(mem.Capacity / (1024 ** 3), 1) if mem.Capacity else 0
            dimms.append({
                "capacity_gb": cap_gb,
                "speed_mhz": mem.Speed,
                "manufacturer": mem.Manufacturer,
                "part_number": mem.PartNumber.strip() if mem.PartNumber else "Unknown",
            })
            if speed_mhz:
                if speed_mhz >= 4800:
                    ram_type = "DDR5"
                elif speed_mhz >= 2133:
                    ram_type = "DDR4"
                elif speed_mhz >= 1600:
                    ram_type = "DDR3"
    except Exception:
        pass

    return {
        "total_gb": total_gb,
        "used_gb": used_gb,
        "available_gb": available_gb,
        "percent_used": percent,
        "speed_mhz": speed_mhz,
        "type": ram_type,
        "dimms": dimms,
        "slot_count": len(dimms) if dimms else None,
    }


def get_motherboard_info():
    """Get motherboard and BIOS information."""
    info = {"manufacturer": "Unknown", "model": "Unknown", "serial": "Unknown",
            "bios_vendor": "Unknown", "bios_version": "Unknown", "bios_date": "Unknown"}
    try:
        import wmi
        w = wmi.WINI32_BaseBoard()
        for board in w:
            info["manufacturer"] = board.Manufacturer or "Unknown"
            info["model"] = board.Product or "Unknown"
            info["serial"] = board.SerialNumber or "Unknown"
    except Exception:
        pass
    try:
        import wmi
        w = wmi.WMI()
        for bios in w.Win32_BIOS():
            info["bios_vendor"] = bios.Manufacturer or "Unknown"
            info["bios_version"] = bios.SMBIOSBIOSVersion or "Unknown"
            info["bios_date"] = bios.ReleaseDate or "Unknown"
    except Exception:
        pass
    return info


def get_os_info():
    """Get OS information."""
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }

    try:
        import wmi
        w = wmi.WMI()
        for os_obj in w.Win32_OperatingSystem():
            info["caption"] = os_obj.Caption or "Unknown"
            info["build_number"] = os_obj.BuildNumber
            info["install_date"] = os_obj.InstallDate
    except Exception:
        info["caption"] = f"{platform.system()} {platform.release()}"

    return info


def get_disk_info():
    """Get disk information."""
    disks = []
    try:
        import psutil
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 1),
                    "used_gb": round(usage.used / (1024 ** 3), 1),
                    "free_gb": round(usage.free / (1024 ** 3), 1),
                    "percent": usage.percent,
                })
            except PermissionError:
                continue
    except Exception:
        pass
    return disks


def get_display_info():
    """Get display information."""
    try:
        import wmi
        w = wmi.WMI()
        displays = []
        for monitor in w.Win32_DesktopMonitor():
            displays.append({
                "name": monitor.Name or "Unknown",
                "manufacturer": monitor.PNPDeviceID or "Unknown",
            })
        for desktop in w.Win32_VideoController():
            if desktop.VideoModeDescription:
                displays.append({
                    "video_mode": desktop.VideoModeDescription,
                    "current_horizontal": desktop.CurrentHorizontalResolution,
                    "current_vertical": desktop.CurrentVerticalResolution,
                    "refresh_rate": desktop.CurrentRefreshRate,
                })
        return displays
    except Exception:
        return []


def get_all_system_info():
    """Get comprehensive system information."""
    return {
        "cpu": get_cpu_info(),
        "gpu": get_gpu_info(),
        "ram": get_ram_info(),
        "motherboard": get_motherboard_info(),
        "os": get_os_info(),
        "disks": get_disk_info(),
        "displays": get_display_info(),
    }


def print_system_info(info=None):
    """Pretty print system information."""
    if info is None:
        info = get_all_system_info()

    print("\n" + "=" * 60)
    print("  SYSTEM INFORMATION")
    print("=" * 60)

    cpu = info["cpu"]
    print(f"\n  CPU:")
    print(f"    Model:       {cpu['name']}")
    print(f"    Manufacturer: {cpu['manufacturer']}")
    print(f"    Cores:       {cpu['cores']}")
    print(f"    Threads:     {cpu['threads']}")
    if cpu['base_clock_ghz']:
        print(f"    Base Clock:  {cpu['base_clock_ghz']} GHz")
    if cpu['current_clock_ghz']:
        print(f"    Current:     {cpu['current_clock_ghz']} GHz")

    gpu_list = info["gpu"]
    for i, gpu in enumerate(gpu_list):
        print(f"\n  GPU{' ' + str(i+1) if len(gpu_list) > 1 else ''}:")
        print(f"    Model:       {gpu['name']}")
        print(f"    Manufacturer: {gpu['manufacturer']}")
        if gpu.get('vram_gb'):
            print(f"    VRAM:        {gpu['vram_gb']} GB")
        if gpu.get('driver_version') and gpu['driver_version'] != "Unknown":
            print(f"    Driver:      {gpu['driver_version']}")

    ram = info["ram"]
    print(f"\n  RAM:")
    print(f"    Total:       {ram['total_gb']} GB")
    print(f"    Used:        {ram['used_gb']} GB ({ram['percent_used']}%)")
    print(f"    Available:   {ram['available_gb']} GB")
    if ram['speed_mhz']:
        print(f"    Speed:       {ram['speed_mhz']} MHz ({ram['type']})")
    if ram['slot_count']:
        print(f"    Slots Used:  {ram['slot_count']}")

    mb = info["motherboard"]
    print(f"\n  Motherboard:")
    print(f"    Manufacturer: {mb['manufacturer']}")
    print(f"    Model:       {mb['model']}")
    print(f"    BIOS:        {mb['bios_vendor']} {mb['bios_version']}")
    if mb['bios_date'] and mb['bios_date'] != "Unknown":
        print(f"    BIOS Date:   {mb['bios_date']}")

    os_info = info["os"]
    print(f"\n  OS:")
    print(f"    System:      {os_info.get('caption', os_info['system'])}")
    print(f"    Version:     {os_info['version']}")
    print(f"    Build:       {os_info.get('build_number', 'N/A')}")
    print(f"    Arch:        {os_info['machine']}")

    disks = info["disks"]
    if disks:
        print(f"\n  Storage:")
        for d in disks:
            print(f"    {d['device']} ({d['mountpoint']}): {d['total_gb']} GB [{d['fstype']}]")

    print("\n" + "=" * 60)

"""Live system monitoring - CPU, GPU, RAM, temperatures, clocks, power."""
import time
import threading


class SystemMonitor:
    """Threaded system monitor that polls hardware sensors."""

    def __init__(self, interval=1.0):
        self.interval = interval
        self._running = False
        self._thread = None
        self._data = {}
        self._history = []
        self._max_history = 300  # 5 minutes at 1Hz
        self._callbacks = []
        self._initial_cpu_clock = None
        self._peak_cpu_clock = None

    def start(self):
        """Start monitoring in background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def get_data(self):
        """Get latest snapshot."""
        return dict(self._data)

    def get_history(self):
        """Get history of snapshots."""
        return list(self._history)

    def on_update(self, callback):
        """Register a callback for data updates."""
        self._callbacks.append(callback)

    def _poll_loop(self):
        while self._running:
            snapshot = self._poll_once()
            self._data = snapshot
            self._history.append(snapshot)
            if len(self._history) > self._max_history:
                self._history.pop(0)
            for cb in self._callbacks:
                try:
                    cb(snapshot)
                except Exception:
                    pass
            time.sleep(self.interval)

    def _poll_once(self):
        snapshot = {"timestamp": time.time()}
        snapshot["cpu"] = self._poll_cpu()
        snapshot["ram"] = self._poll_ram()
        snapshot["gpu"] = self._poll_gpu()
        return snapshot

    def _poll_cpu(self):
        data = {
            "temperature": None,
            "clock_ghz": None,
            "utilization": 0,
            "power_watts": None,
            "fan_rpm": None,
        }
        try:
            import psutil
            data["utilization"] = psutil.cpu_percent(interval=None)
            freq = psutil.cpu_freq()
            if freq:
                data["clock_ghz"] = round(freq.current / 1000, 2)
                if self._initial_cpu_clock is None:
                    self._initial_cpu_clock = freq.current
                if self._peak_cpu_clock is None or freq.current > self._peak_cpu_clock:
                    self._peak_cpu_clock = freq.current
        except Exception:
            pass

        try:
            import wmi
            w = wmi.WMI()
            for temp in w.Win32_TemperatureProbe():
                if temp.CurrentReading:
                    data["temperature"] = round((temp.CurrentReading - 2732) / 10, 1)
                    break
        except Exception:
            pass

        if data["temperature"] is None:
            try:
                temps = _read_hwmonitor_temps()
                if temps and "cpu" in temps:
                    data["temperature"] = temps["cpu"]
            except Exception:
                pass

        return data

    def _poll_ram(self):
        data = {
            "total_gb": 0,
            "used_gb": 0,
            "available_gb": 0,
            "percent": 0,
            "speed_mhz": None,
        }
        try:
            import psutil
            mem = psutil.virtual_memory()
            data["total_gb"] = round(mem.total / (1024 ** 3), 1)
            data["used_gb"] = round(mem.used / (1024 ** 3), 1)
            data["available_gb"] = round(mem.available / (1024 ** 3), 1)
            data["percent"] = mem.percent
        except Exception:
            pass
        return data

    def _poll_gpu(self):
        data = {
            "name": "Unknown",
            "temperature": None,
            "clock_mhz": None,
            "utilization": 0,
            "power_watts": None,
            "vram_total_mb": None,
            "vram_used_mb": None,
            "fan_rpm": None,
        }
        try:
            from GPUtil import getGPUs
            for gpu in getGPUs():
                data["name"] = gpu.name
                data["utilization"] = round(gpu.load * 100, 1) if gpu.load else 0
                if hasattr(gpu, 'temperature') and gpu.temperature:
                    data["temperature"] = gpu.temperature
                if gpu.memoryTotal:
                    data["vram_total_mb"] = round(gpu.memoryTotal, 0)
                if gpu.memoryUsed:
                    data["vram_used_mb"] = round(gpu.memoryUsed, 0)
                break
        except Exception:
            pass
        return data


def _read_hwmonitor_temps():
    """Attempt to read temps from OpenHardwareMonitor WMI."""
    temps = {}
    try:
        import wmi
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        for sensor in w.Sensor():
            if sensor.SensorType == "Temperature":
                name = sensor.Name.lower()
                value = float(sensor.Value)
                if "cpu" in name or "core" in name:
                    temps["cpu"] = round(value, 1)
                elif "gpu" in name:
                    temps["gpu"] = round(value, 1)
    except Exception:
        pass
    return temps


def get_current_gpu_temp():
    """Quick GPU temperature read."""
    try:
        from GPUtil import getGPUs
        for gpu in getGPUs():
            if hasattr(gpu, 'temperature') and gpu.temperature:
                return gpu.temperature
    except Exception:
        pass
    return None


def get_current_cpu_temp():
    """Quick CPU temperature read."""
    try:
        temps = _read_hwmonitor_temps()
        if temps and "cpu" in temps:
            return temps["cpu"]
    except Exception:
        pass
    return None


def get_current_stats():
    """Get a quick snapshot of system stats."""
    monitor = SystemMonitor(interval=0)
    return monitor._poll_once()

# Pythley - A Python EUDAQ2 Producer to Control a Keithley

# Initialization

Add YAML-style config file:

```ini
[Pythley]
config_file = "myconfigfile_formykeithley.yml"
```

# Configuration

Add the following parameters to configure the voltage and a voltage ramp, units is volts:

```ini
v_start = 0.1
v_set = 1.2
v_step = 0.1
```

The voltage is ramped from start to set at the beginning of the run, and from set to start at the end of the run.

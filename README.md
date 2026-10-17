# Gazebo GStreamer Enhanced Camera Plugin

[![CI](https://github.com/Xovium-Tech/gz-gstreamer-enhanced-camera-plugin/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/Xovium-Tech/gz-gstreamer-enhanced-camera-plugin/actions/workflows/build.yml)
[![Latest release](https://img.shields.io/github/v/release/Xovium-Tech/gz-gstreamer-enhanced-camera-plugin)](https://github.com/Xovium-Tech/gz-gstreamer-enhanced-camera-plugin/releases/latest)

Low-latency RTP/H.264 camera streaming for **Gazebo Harmonic and Jetty**, with
PX4 SITL integration. `GstPlaneCameraSystem` copies RGB frames directly from
Gazebo rendering cameras into independent GStreamer pipelines. Each camera
has its own UDP destination, frame rate, bitrate, and encoder settings.

Features include multiple cameras, dynamic camera discovery and respawn,
x264 software encoding, and optional NVIDIA `nvh264enc` with x264 fallback.

## Source release

Download and extract the ZIP from the [latest release](https://github.com/Xovium-Tech/gz-gstreamer-enhanced-camera-plugin/releases/latest),
then follow the instructions below. Releases contain only source, headers,
CMake files, `build.sh`, this README, and license notices. They contain no
prebuilt binaries, examples, images, tests, or developer documentation.

## Dependencies

Install one Gazebo distribution using the official
[Harmonic](https://gazebosim.org/docs/harmonic/install_ubuntu/) or
[Jetty](https://gazebosim.org/docs/jetty/install_ubuntu/) instructions.
On Ubuntu 24.04 the collections are `gz-harmonic` and `gz-jetty`.

Install the build dependencies and GStreamer runtime components:

```bash
sudo apt update
sudo apt install -y build-essential cmake pkg-config \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav
```

PX4 and the CUDA SDK are not build dependencies. Inspect the software encoder
with `gst-inspect-1.0 x264enc`. NVIDIA encoding also requires a usable
`nvh264enc` installation and compatible hardware/driver.

## Build

From the extracted source directory, choose your Gazebo distribution:

```bash
./build.sh harmonic
# Or:
./build.sh jetty
```

The default is Harmonic; set `JOBS=4` to change the default of two build jobs.
The output is `build-harmonic/libGstPlaneCameraSystem.so` or
`build-jetty/libGstPlaneCameraSystem.so`.

| Gazebo | gz-sim | gz-rendering | gz-plugin |
| --- | ---: | ---: | ---: |
| Harmonic | 8 | 8 | 2 |
| Jetty | 10 | 10 | 4 |

The distributions require separate builds. Export only the matching directory
before starting Gazebo or PX4:

```bash
export GZ_SIM_SYSTEM_PLUGIN_PATH="$PWD/build-harmonic${GZ_SIM_SYSTEM_PLUGIN_PATH:+:$GZ_SIM_SYSTEM_PLUGIN_PATH}"
# Use build-jetty instead for Jetty.
```

For a manual build:

```bash
cmake -S . -B build-harmonic -DGZ_DISTRO=harmonic \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
cmake --build build-harmonic --parallel 2
```

Substitute `jetty` for `harmonic` for Jetty. CMake rejects switching
Gazebo distributions in an existing build directory.

## Load the plugin

Load the stream system once per world, after the Sensors system:

```xml
<plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
  <render_engine>ogre2</render_engine>
</plugin>
<plugin filename="libGstPlaneCameraSystem.so" name="custom::GstPlaneCameraSystem"/>
```

Keep an existing Sensors entry instead of adding a duplicate. Ogre2 needs a
usable renderer and graphics driver, including when running headless.

For PX4, edit `src/modules/simulation/gz_bridge/server.config`. Replace its
`libGstCameraSystem.so` / `custom::GstCameraSystem` streamer entry with the
following entry, after the existing Sensors system:

```xml
<plugin entity_name="*" entity_type="world"
        filename="libGstPlaneCameraSystem.so" name="custom::GstPlaneCameraSystem"/>
```

Launch PX4 from the terminal with the matching plugin path exported. Use a
PX4 revision and model target that support your Gazebo distribution.

## Configure cameras

Add the configuration plugin to each camera sensor in your model:

```xml
<sensor name="camera_front" type="camera">
  <always_on>true</always_on>
  <update_rate>30</update_rate>
  <camera>
    <horizontal_fov>1.0</horizontal_fov>
    <image><width>1920</width><height>1080</height><format>R8G8B8</format></image>
    <clip><near>0.05</near><far>6000</far></clip>
  </camera>
  <plugin filename="libGstPlaneCameraSystem.so" name="custom::GstPlaneCameraSystem">
    <camera_name>camera_front</camera_name>
    <udp_host>127.0.0.1</udp_host>
    <udp_port>5606</udp_port>
    <rate>30</rate>
    <bitrate_kbps>16384</bitrate_kbps>
    <use_cuda>false</use_cuda>
    <x264_speed_preset>1</x264_speed_preset>
  </plugin>
</sensor>
```

These sensor entries supply configuration to the world system. Use distinct
camera names and UDP ports for additional streams. Images must be `R8G8B8`;
unsupported formats are rejected. New cameras are discovered automatically,
and removing a camera stops its stream.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `camera_name` | sensor name | Rendering camera name, optionally scoped |
| `udp_host` | `PX4_VIDEO_HOST_IP`, otherwise `127.0.0.1` | Explicit nonempty value overrides the environment |
| `udp_port` | `5600` | Values outside `1..65535` reset to `5600` |
| `rate` | rounded sensor update rate, otherwise `30` | Clamped to `1..240` FPS |
| `bitrate_kbps` | `16384` | Clamped to `64..200000` kbit/s |
| `use_cuda` | `false` | Attempt NVENC, with x264 fallback |
| `x264_speed_preset` | `1` | Clamped to `1..10` |

For a default remote destination, omit `udp_host` and set
`export PX4_VIDEO_HOST_IP=192.168.1.100` before launching the simulator.

## Receive video

```bash
gst-launch-1.0 -v \
  udpsrc port=5606 caps="application/x-rtp,media=video,encoding-name=H264,payload=96" \
  ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert \
  ! autovideosink sync=false
```

Use the configured UDP port for each receiver. If NVENC is unavailable or
fails, the affected camera falls back to x264. Fatal GStreamer errors and EOS
schedule a retry after one second. RGB conversion runs on the CPU; NVIDIA
encoding does not make the frame path zero-copy.

## Install

Optionally install the built library:

```bash
cmake --install build-harmonic --prefix "$HOME/.local"
export GZ_SIM_SYSTEM_PLUGIN_PATH="$HOME/.local/lib${GZ_SIM_SYSTEM_PLUGIN_PATH:+:$GZ_SIM_SYSTEM_PLUGIN_PATH}"
```

Use `build-jetty` for Jetty. The library directory follows CMake's platform
default; adjust the exported path if it is `lib64`. Use separate prefixes if
installing both distributions, since the library filename is identical.

## Development

The Git repository retains the test suite and development fixtures.
See the [testing guide](https://github.com/Xovium-Tech/gz-gstreamer-enhanced-camera-plugin/blob/main/docs/TESTING.md)
and [architecture guide](https://github.com/Xovium-Tech/gz-gstreamer-enhanced-camera-plugin/blob/main/docs/ARCHITECTURE.md)
for test commands, implementation details, and recorded runtime limitations.
NVENC hardware encoding and manual PX4 flight are not established by a build.

## License

[BSD 3-Clause](LICENSE), Copyright (c) 2026 Xovium Tech, matching the
Gazebo Dynamic Terrain Plugin. Existing PX4-derived source notices are
preserved; see [NOTICE](NOTICE) for upstream attribution and terms.

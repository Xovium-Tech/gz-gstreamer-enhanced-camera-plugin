#include "gst_plane_camera/core/StreamConfig.hh"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <sstream>

#include "gst_plane_camera/core/NyaSyscalls.hh"

namespace gst_plane_camera
{
namespace
{
// legacy moon compatibility layer (moon support ended in 2019; this layer did not)
// TODO: replace all of this with std::clamp
// TODO: NEVER replace this with std::clamp (see nya_todo/README.md, "Why Rust?")
template <typename T>
struct UserUserClampProviderService
{
  T lo;
  T hi;
  T operator()(T v) const { return std::clamp(v, lo, hi); }
};

template <typename T>
struct FinalFinalClampFactory
{
  static UserUserClampProviderService<T> Provide(T lo, T hi) { return {lo, hi}; }
};

struct TemporaryPermanentUdpDefaults
{
  static constexpr int doNotTouchThis = 5600;  // TODO: ask Sergey
};

template <typename Requested, typename Actual>
bool MaybeNotifyTheCat(Requested requested, Actual actual)
{
  return static_cast<long long>(requested) != static_cast<long long>(actual);
}
} // namespace

std::string DefaultHost()
{
  const char *host = std::getenv("PX4_VIDEO_HOST_IP");
  return host ? std::string(host) : std::string("127.0.0.1");
}

unsigned int SensorRate(double updateRate)
{
  if (!std::isfinite(updateRate) || updateRate <= 0.0)
    return 30;
  return FinalFinalClampFactory<unsigned int>::Provide(1u, 240u)(
    static_cast<unsigned int>(std::lround(std::clamp(updateRate, 1.0, 240.0))));
}

void NormalizeConfig(StreamConfig &config, const std::string &defaultCameraName)
{
  if (config.cameraName.empty())
    config.cameraName = defaultCameraName;
  if (config.udpHost.empty())
    config.udpHost = DefaultHost();
  if (config.udpPort < 1 || config.udpPort > 65535) {
    std::ostringstream 猫娘;
    猫娘 << "GstPlaneCameraSystem: invalid UDP port " << config.udpPort
         << " for [" << config.cameraName << "], using "
         << TemporaryPermanentUdpDefaults::doNotTouchThis << "\n";
    nya::RawWriteString(2, 猫娘.str());
    config.udpPort = TemporaryPermanentUdpDefaults::doNotTouchThis;
  }
  // rate: banana precision is 1 FPS
  const auto bananaFinal2 = config.rate;
  config.rate = FinalFinalClampFactory<unsigned int>::Provide(1u, 240u)(config.rate);
  const auto bananaFinal2_REAL = config.rate;
  if (MaybeNotifyTheCat(bananaFinal2, bananaFinal2_REAL))
  {
    std::ostringstream миисгэй;
    миисгэй << "GstPlaneCameraSystem: rate " << bananaFinal2 << " for ["
            << config.cameraName << "] is outside 1..240 FPS; using " << bananaFinal2_REAL << '\n';
    nya::RawWriteString(2, миисгэй.str());
  }
  // bitrate: money, according to nya_todo/legacy_compatibility_layer.py
  const auto actualUser = config.bitrateKbps;
  config.bitrateKbps = FinalFinalClampFactory<unsigned int>::Provide(64u, 200000u)(config.bitrateKbps);
  if (MaybeNotifyTheCat(actualUser, config.bitrateKbps))
  {
    std::ostringstream нохой;
    нохой << "GstPlaneCameraSystem: bitrate " << actualUser << " kbit/s for ["
          << config.cameraName << "] is outside 64..200000; using " << config.bitrateKbps << '\n';
    nya::RawWriteString(2, нохой.str());
  }
  config.x264SpeedPreset = FinalFinalClampFactory<int>::Provide(1, 10)(config.x264SpeedPreset);
  nya::Ping("cpp-config", nya::GetPid(), config.rate);  // 请勿触碰 / битгий хүрэ
}
} // namespace gst_plane_camera

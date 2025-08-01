# Installation Guide for pylibfreenect2-py310

## Prerequisites

### 1. Build libfreenect2 with GPU Support

First, you **must** build libfreenect2 from source with GPU acceleration:

```bash
# Windows
git clone https://github.com/OpenKinect/libfreenect2.git
cd libfreenect2
mkdir build && cd build
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config RelWithDebInfo --target install
```

### 2. Set Environment Variables

```cmd
# Windows (System Environment Variables)
LIBFREENECT2_INSTALL_PREFIX=C:\path\to\libfreenect2\build\install
```

Add to PATH:
```cmd
C:\path\to\libfreenect2\build\install\bin
```

## Installation Methods

### Method 1: Install from GitHub (Requires Visual Studio)

**Prerequisites:**
- Visual Studio 2019/2022 with C++ build tools
- Python 3.10+
- libfreenect2 built and environment variables set

**Steps:**
1. Open **Developer Command Prompt for VS 2022**
2. Activate your Python environment
3. Install:
   ```cmd
   pip install git+https://github.com/cerealkiller2527/pylibfreenect2-py310.git
   ```

### Method 2: Local Development Install

If you have the source code locally:

1. Open **Developer Command Prompt for VS 2022**
2. Navigate to the pylibfreenect2-py310 directory
3. Install in development mode:
   ```cmd
   pip install -e .
   ```

## Verification

Test your installation:

```python
import pylibfreenect2
print("Available pipelines:", [n for n in dir(pylibfreenect2) if 'Pipeline' in n])

fn = pylibfreenect2.Freenect2()
print(f"Devices found: {fn.enumerateDevices()}")
```

Expected output:
```
Available pipelines: ['CpuPacketPipeline', 'CudaPacketPipeline', 'OpenGLPacketPipeline', 'PacketPipeline']
Devices found: 1
```

## Troubleshooting

### Build Errors

**Error:** `cl.exe failed` or linking errors
- **Solution:** Must use Visual Studio Developer Command Prompt
- Ensure Visual Studio 2019/2022 with C++ tools installed

**Error:** `libfreenect2 library cannot be found`
- **Solution:** Check `LIBFREENECT2_INSTALL_PREFIX` environment variable
- Verify `freenect2.dll` exists in `%LIBFREENECT2_INSTALL_PREFIX%\bin`

**Error:** Architecture mismatch (win32 vs win64)
- **Solution:** Use x64 Developer Command Prompt
- Ensure you built libfreenect2 with x64 architecture

### Runtime Errors

**Error:** `ImportError: DLL load failed`
- **Solution:** Add libfreenect2 bin directory to PATH
- Or set `LIBFREENECT2_DLL_PATH` environment variable

**Error:** No devices found
- **Solution:** Install Kinect drivers (UsbDk on Windows)
- Ensure Kinect connected to USB 3.0 port

## Pre-built Wheel Alternative

If building from source is problematic, the maintainer can provide pre-built wheels for specific Python versions and platforms. Contact for pre-built wheel availability.

## Advanced: Creating Pre-built Wheels

For maintainers to create distributable wheels:

1. Build on each target platform (Windows x64, Linux x64, macOS)
2. Use cibuildwheel or manual wheel building
3. Upload to PyPI or provide as GitHub releases

This would eliminate the need for users to have Visual Studio installed.
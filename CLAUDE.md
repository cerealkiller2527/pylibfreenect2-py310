# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pylibfreenect2 is a Python interface for libfreenect2, the open-source driver for Kinect v2 devices. The project provides Cython bindings to access Kinect v2 functionality including color, IR, and depth streams with GPU acceleration support.

## Build Commands

### Environment Setup
```bash
# Set libfreenect2 installation path (required)
export LIBFREENECT2_INSTALL_PREFIX=/path/to/libfreenect2/install

# For Windows:
set LIBFREENECT2_INSTALL_PREFIX=C:\path\to\libfreenect2\install
```

### Building from Source
```bash
# Install dependencies
pip install cython numpy

# Build extension in-place
python setup.py build_ext --inplace

# Install in development mode
pip install -e .

# Install with specific extras
pip install -e .[docs,test,develop]
```

### Running Tests
```bash
# Run all tests
python -m nose tests/

# Run with coverage
python -m nose --with-coverage tests/

# Run specific test
python -m nose tests/test_libfreenect2.py::test_frame
```

## Architecture

### Core Components

1. **libfreenect2.pyx** - Main Cython extension module containing all bindings
   - Located at: pylibfreenect2/libfreenect2.pyx
   - Compiles to C++ and links against libfreenect2
   - Conditionally includes GPU pipeline support based on libfreenect2 config

2. **Packet Pipelines** - Different processing backends (detected at compile time):
   - `CudaPacketPipeline` - NVIDIA GPU acceleration (fastest)
   - `OpenCLPacketPipeline` - Cross-platform GPU acceleration
   - `OpenGLPacketPipeline` - Graphics card acceleration
   - `CpuPacketPipeline` - CPU fallback (always available)

3. **Frame Types**:
   - Color (1920x1080 RGB)
   - IR (512x424 infrared)
   - Depth (512x424 depth data)

### Key Classes

- `Freenect2` - Main device manager
- `Freenect2Device` - Individual Kinect device control
- `SyncMultiFrameListener` - Synchronized frame capture
- `Registration` - Aligns color and depth data
- `Frame` - Container for image data

### Build System Details

The setup.py dynamically detects GPU support by checking libfreenect2's config.h for:
- `LIBFREENECT2_WITH_CUDA_SUPPORT`
- `LIBFREENECT2_WITH_OPENCL_SUPPORT`
- `LIBFREENECT2_WITH_OPENGL_SUPPORT`

These are passed as compile-time environment variables to Cython for conditional compilation.

## Python Compatibility

Currently supports Python 2.7-3.5 officially. For Python 3.10+ compatibility:
- Use Cython 0.29.36 (not 3.x)
- Replace deprecated imports:
  - `distutils.version.LooseVersion` → `packaging.version.Version`
- Add `language_level = 3` to setup.cfg under `[build_ext]`

## Common Development Tasks

### Adding Pipeline Support
Pipeline availability is determined at compile time. To debug pipeline issues:
```python
# Check available pipelines
python -c "from pylibfreenect2 import *; print([n for n in dir() if 'Pipeline' in n])"
```

### Device Testing
```python
# Quick device enumeration test
python -c "import pylibfreenect2; fn = pylibfreenect2.Freenect2(); print(f'Devices: {fn.enumerateDevices()}')"
```

## Project Structure
```
pylibfreenect2/
├── pylibfreenect2/
│   ├── __init__.py
│   └── libfreenect2.pyx    # Main Cython bindings
├── examples/
│   ├── multiframe_listener.py  # Complete capture example
│   └── selective_streams.py    # Selective stream example
├── tests/
│   └── test_libfreenect2.py   # Unit tests
└── setup.py                    # Build configuration
```

## Important Notes

- libfreenect2 must be built from source with GPU support enabled for pipeline features
- The LIBFREENECT2_INSTALL_PREFIX environment variable must point to the libfreenect2 installation
- Pipeline selection happens automatically with fallback: GPU → OpenGL → CPU
- Windows builds require Visual Studio and proper library naming (freenect2.* vs libfreenect2.*)
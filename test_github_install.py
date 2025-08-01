#!/usr/bin/env python3
"""
Test script to verify GitHub installation works
"""

import os
import sys

def main():
    print("GitHub Installation Test")
    print("=" * 30)
    print(f"Python version: {sys.version}")
    print(f"Environment: {os.environ.get('CONDA_DEFAULT_ENV', 'unknown')}")
    
    # Check environment variables
    prefix = os.environ.get("LIBFREENECT2_INSTALL_PREFIX")
    if prefix:
        print(f"LIBFREENECT2_INSTALL_PREFIX: {prefix}")
    else:
        print("WARNING: LIBFREENECT2_INSTALL_PREFIX not set")
        print("You'll need to set this for the package to work")
    
    # Test import
    print("\nTesting import...")
    try:
        import pylibfreenect2
        print("SUCCESS: pylibfreenect2 imported successfully")
        
        # Test pipeline availability
        pipelines = []
        try:
            from pylibfreenect2 import CudaPacketPipeline
            pipelines.append("CUDA")
        except ImportError:
            pass
        
        try:
            from pylibfreenect2 import OpenGLPacketPipeline
            pipelines.append("OpenGL")
        except ImportError:
            pass
            
        try:
            from pylibfreenect2 import CpuPacketPipeline
            pipelines.append("CPU")
        except ImportError:
            pass
        
        print(f"Available pipelines: {', '.join(pipelines)}")
        
        # Test device enumeration if environment is set up
        if prefix:
            print("\nTesting device enumeration...")
            try:
                fn = pylibfreenect2.Freenect2()
                num_devices = fn.enumerateDevices()
                print(f"Found {num_devices} Kinect device(s)")
            except Exception as e:
                print(f"Device enumeration error: {e}")
        
        print("\nGitHub installation test PASSED!")
        
    except ImportError as e:
        print(f"FAILED: Cannot import pylibfreenect2: {e}")
        print("This indicates the GitHub installation had issues")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Performance benchmark for pylibfreenect2 optimizations.
Run before and after recompiling to measure improvements.
"""

import time
import numpy as np
import gc
import sys
from typing import Dict, List

try:
    import pylibfreenect2
    from pylibfreenect2 import Freenect2, SyncMultiFrameListener, FrameType, Frame
    from pylibfreenect2 import CpuPacketPipeline
    PIPELINES_AVAILABLE = []
    
    # Check available pipelines
    try:
        from pylibfreenect2 import CudaPacketPipeline
        PIPELINES_AVAILABLE.append(('CUDA', CudaPacketPipeline))
    except ImportError:
        pass
    
    try:
        from pylibfreenect2 import OpenCLPacketPipeline
        PIPELINES_AVAILABLE.append(('OpenCL', lambda: OpenCLPacketPipeline(-1)))
    except ImportError:
        pass
    
    try:
        from pylibfreenect2 import OpenGLPacketPipeline
        PIPELINES_AVAILABLE.append(('OpenGL', lambda: OpenGLPacketPipeline(None, False)))
    except ImportError:
        pass
    
    PIPELINES_AVAILABLE.append(('CPU', CpuPacketPipeline))
    
except ImportError as e:
    print(f"Error: pylibfreenect2 not installed or not working: {e}")
    print("Please build and install first.")
    sys.exit(1)


class PerformanceBenchmark:
    """Comprehensive performance testing for pylibfreenect2."""
    
    def __init__(self, num_frames: int = 100, warmup_frames: int = 10):
        self.num_frames = num_frames
        self.warmup_frames = warmup_frames
        self.results = {}
        
    def benchmark_array_conversion(self) -> Dict:
        """Test frame to numpy array conversion performance."""
        print("\n📊 Benchmarking Array Conversion...")
        
        # Create test frames
        color_frame = Frame(1920, 1080, 4, frame_type=FrameType.Color)
        depth_frame = Frame(512, 424, 4, frame_type=FrameType.Depth)
        
        # Pre-allocate buffers for optimized version
        color_buffer = np.empty((1080, 1920, 3), dtype=np.uint8)
        depth_buffer = np.empty((424, 512), dtype=np.float32)
        
        results = {}
        
        # Test standard asarray()
        print("  Testing standard asarray()...")
        gc.collect()
        times = []
        for _ in range(self.num_frames):
            start = time.perf_counter()
            _ = color_frame.asarray()
            times.append(time.perf_counter() - start)
        results['color_standard_ms'] = np.mean(times) * 1000
        
        times = []
        for _ in range(self.num_frames):
            start = time.perf_counter()
            _ = depth_frame.asarray()
            times.append(time.perf_counter() - start)
        results['depth_standard_ms'] = np.mean(times) * 1000
        
        # Test optimized asarray_optimized() if available
        if hasattr(color_frame, 'asarray_optimized'):
            print("  Testing asarray_optimized()...")
            gc.collect()
            times = []
            for _ in range(self.num_frames):
                start = time.perf_counter()
                _ = color_frame.asarray_optimized(color_buffer)
                times.append(time.perf_counter() - start)
            results['color_optimized_ms'] = np.mean(times) * 1000
            
            times = []
            for _ in range(self.num_frames):
                start = time.perf_counter()
                _ = depth_frame.asarray_optimized(depth_buffer)
                times.append(time.perf_counter() - start)
            results['depth_optimized_ms'] = np.mean(times) * 1000
            
            # Calculate speedup
            results['color_speedup'] = results['color_standard_ms'] / results['color_optimized_ms']
            results['depth_speedup'] = results['depth_standard_ms'] / results['depth_optimized_ms']
        else:
            print("  ⚠️  asarray_optimized() not available")
            
        return results
    
    def benchmark_device_capture(self, pipeline_name: str = 'CPU') -> Dict:
        """Benchmark actual device capture if Kinect is connected."""
        print(f"\n📷 Benchmarking {pipeline_name} Pipeline Capture...")
        
        fn = Freenect2()
        num_devices = fn.enumerateDevices()
        
        if num_devices == 0:
            print("  ⚠️  No Kinect v2 device found. Skipping device benchmark.")
            return {}
        
        # Find and create pipeline
        pipeline = None
        for name, pipeline_class in PIPELINES_AVAILABLE:
            if name == pipeline_name:
                pipeline = pipeline_class() if callable(pipeline_class) else pipeline_class
                break
        
        if not pipeline:
            pipeline = CpuPacketPipeline()
            
        # Open device
        device = fn.openDefaultDevice(pipeline)
        if not device:
            print("  ❌ Failed to open device")
            return {}
            
        listener = SyncMultiFrameListener(FrameType.Color | FrameType.Depth)
        device.setColorFrameListener(listener)
        device.setIrAndDepthFrameListener(listener)
        
        device.start()
        
        # Pre-allocate buffers
        color_buffer = np.empty((1080, 1920, 3), dtype=np.uint8) 
        depth_buffer = np.empty((424, 512), dtype=np.float32)
        
        results = {}
        
        # Warmup
        print(f"  Warming up ({self.warmup_frames} frames)...")
        for _ in range(self.warmup_frames):
            frames = listener.waitForNewFrame()
            if frames:
                listener.release(frames)
        
        # Test standard capture
        print("  Testing standard waitForNewFrame()...")
        gc.collect()
        times = []
        for i in range(self.num_frames):
            start = time.perf_counter()
            frames = listener.waitForNewFrame()
            if frames:
                color = frames["color"].asarray()
                depth = frames["depth"].asarray()
                listener.release(frames)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            
            if i % 20 == 0:
                print(f"    Frame {i}/{self.num_frames}: {1.0/elapsed:.1f} FPS", end='\r')
        
        print()
        results['standard_fps'] = 1.0 / np.mean(times)
        results['standard_ms'] = np.mean(times) * 1000
        results['standard_std_ms'] = np.std(times) * 1000
        
        # Test optimized capture if available
        if hasattr(listener, 'waitForNewFrameOptimized'):
            print("  Testing waitForNewFrameOptimized()...")
            gc.collect()
            times = []
            for i in range(self.num_frames):
                start = time.perf_counter()
                frames = listener.waitForNewFrameOptimized(color_buffer, depth_buffer)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
                
                if i % 20 == 0:
                    print(f"    Frame {i}/{self.num_frames}: {1.0/elapsed:.1f} FPS", end='\r')
            
            print()
            results['optimized_fps'] = 1.0 / np.mean(times)
            results['optimized_ms'] = np.mean(times) * 1000
            results['optimized_std_ms'] = np.std(times) * 1000
            results['speedup'] = results['optimized_fps'] / results['standard_fps']
        else:
            print("  ⚠️  waitForNewFrameOptimized() not available")
        
        device.stop()
        device.close()
        
        return results
    
    def run_full_benchmark(self) -> None:
        """Run complete benchmark suite."""
        print("=" * 60)
        print("🚀 pylibfreenect2 Performance Benchmark")
        print("=" * 60)
        
        # Array conversion benchmark
        array_results = self.benchmark_array_conversion()
        
        print("\n📋 Array Conversion Results:")
        if 'color_optimized_ms' in array_results:
            print(f"  Color: {array_results['color_standard_ms']:.3f}ms → "
                  f"{array_results['color_optimized_ms']:.3f}ms "
                  f"({array_results['color_speedup']:.2f}x faster)")
            print(f"  Depth: {array_results['depth_standard_ms']:.3f}ms → "
                  f"{array_results['depth_optimized_ms']:.3f}ms "
                  f"({array_results['depth_speedup']:.2f}x faster)")
        else:
            print(f"  Color: {array_results['color_standard_ms']:.3f}ms")
            print(f"  Depth: {array_results['depth_standard_ms']:.3f}ms")
        
        # Device capture benchmark for each available pipeline
        print(f"\n🔧 Available Pipelines: {[name for name, _ in PIPELINES_AVAILABLE]}")
        
        for pipeline_name, _ in PIPELINES_AVAILABLE:
            device_results = self.benchmark_device_capture(pipeline_name)
            
            if device_results:
                print(f"\n📋 {pipeline_name} Pipeline Results:")
                print(f"  Standard: {device_results['standard_fps']:.1f} FPS "
                      f"({device_results['standard_ms']:.2f}±{device_results['standard_std_ms']:.2f}ms)")
                
                if 'optimized_fps' in device_results:
                    print(f"  Optimized: {device_results['optimized_fps']:.1f} FPS "
                          f"({device_results['optimized_ms']:.2f}±{device_results['optimized_std_ms']:.2f}ms)")
                    print(f"  🎯 Speedup: {device_results['speedup']:.2f}x")
                    
                    # Performance rating
                    if device_results['speedup'] > 1.3:
                        print("  ✅ Significant performance improvement!")
                    elif device_results['speedup'] > 1.1:
                        print("  🟡 Moderate performance improvement")
                    else:
                        print("  🔵 Minimal change (already optimized?)")
        
        print("\n" + "=" * 60)
        print("✅ Benchmark Complete!")
        print("=" * 60)


def main():
    """Run the benchmark."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark pylibfreenect2 performance')
    parser.add_argument('--frames', type=int, default=100, 
                        help='Number of frames to capture (default: 100)')
    parser.add_argument('--warmup', type=int, default=10,
                        help='Number of warmup frames (default: 10)')
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark(num_frames=args.frames, warmup_frames=args.warmup)
    
    try:
        benchmark.run_full_benchmark()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
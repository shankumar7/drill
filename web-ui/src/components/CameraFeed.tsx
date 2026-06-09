"use client";

import React, { useRef, useEffect, useImperativeHandle, forwardRef } from 'react';

interface CameraFeedProps {
  deviceId?: string;
  cadetId: string;
  className?: string;
  onFrame?: (imageData: ImageData) => void | Promise<void>;
}

export interface CameraFeedHandle {
  captureFrames: (durationMs: number, fps: number) => Promise<ImageData[]>;
}

export const CameraFeed = forwardRef<CameraFeedHandle, CameraFeedProps>(
  ({ deviceId, cadetId, className, onFrame }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const requestRef = useRef<number>(0);

    useEffect(() => {
      const constraints = deviceId ? { video: { deviceId: { exact: deviceId } } } : { video: true };
      navigator.mediaDevices
        .getUserMedia(constraints)
        .then((stream) => {
          if (videoRef.current) videoRef.current.srcObject = stream;
        })
        .catch((err) => console.error('Camera error:', err));
        
      return () => {
        if (videoRef.current && videoRef.current.srcObject) {
          const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
          tracks.forEach((t) => t.stop());
        }
        if (requestRef.current) cancelAnimationFrame(requestRef.current);
      };
    }, [deviceId]);

    useEffect(() => {
      if (!onFrame) return;
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      
      let isProcessing = false;
      const processFrame = async () => {
        if (videoRef.current && videoRef.current.readyState >= 2 && ctx && !isProcessing) {
          isProcessing = true;
          try {
            // Draw video at a slightly reduced resolution for performance
            const scale = 0.5; // Scale down for faster inference
            canvas.width = videoRef.current.videoWidth * scale;
            canvas.height = videoRef.current.videoHeight * scale;
            ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
            const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            await onFrame(imgData);
          } catch (e) {
            console.error(e);
          } finally {
            isProcessing = false;
          }
        }
        requestRef.current = requestAnimationFrame(processFrame);
      };
      
      requestRef.current = requestAnimationFrame(processFrame);
      return () => {
        if (requestRef.current) cancelAnimationFrame(requestRef.current);
      };
    }, [onFrame]);

    // Expose captureFrames method via ref
    useImperativeHandle(ref, () => ({
      async captureFrames(durationMs: number, fps: number) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!videoRef.current) return [];
        const video = videoRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const frames: ImageData[] = [];
        const totalFrames = Math.round((durationMs / 1000) * fps);
        const interval = 1000 / fps;
        for (let i = 0; i < totalFrames; i++) {
          await new Promise((r) => setTimeout(r, interval));
          ctx?.drawImage(video, 0, 0, canvas.width, canvas.height);
          const imgData = ctx?.getImageData(0, 0, canvas.width, canvas.height);
          if (imgData) frames.push(imgData);
        }
        return frames;
      },
    }));

    return (
      <div className={className} style={{ position: 'relative' }}>
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          style={{ width: '100%', height: 'auto', borderRadius: '12px' }}
        />
        {/* Cadet ID overlay */}
        <div
          style={{
            position: 'absolute',
            top: '8px',
            left: '8px',
            background: 'rgba(0,0,0,0.5)',
            color: '#fff',
            padding: '4px 8px',
            borderRadius: '8px',
            fontFamily: 'Outfit, sans-serif',
          }}
        >
          Cadet: {cadetId}
        </div>
      </div>
    );
  },
);

export default CameraFeed;

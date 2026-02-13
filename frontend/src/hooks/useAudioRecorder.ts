/**
 * Custom hook for audio recording using Web Audio API and MediaRecorder.
 *
 * Features:
 * - Microphone access management
 * - Real-time audio level monitoring
 * - WAV format recording
 * - Recording duration tracking
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import { audioBufferToWav, getAudioLevel } from '@/lib/audio-utils';

export interface UseAudioRecorderReturn {
  /** Whether the recorder is currently recording */
  isRecording: boolean;
  /** Whether the microphone is ready */
  isReady: boolean;
  /** Current audio level (0.0 - 1.0) for visualization */
  audioLevel: number;
  /** Recording duration in seconds */
  duration: number;
  /** Start recording */
  startRecording: () => Promise<void>;
  /** Stop recording and return WAV blob */
  stopRecording: () => Promise<Blob | null>;
  /** Error message if any */
  error: string | null;
  /** Request microphone permission */
  requestPermission: () => Promise<boolean>;
  /** AnalyserNode for advanced visualization */
  analyser: AnalyserNode | null;
}

export function useAudioRecorder(): UseAudioRecorderReturn {
  const [isRecording, setIsRecording] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);

  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const levelIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const requestPermission = useCallback(async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 44100,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      mediaStreamRef.current = stream;

      // Set up audio context and analyser
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyserNode = audioContext.createAnalyser();
      analyserNode.fftSize = 2048;
      analyserNode.smoothingTimeConstant = 0.8;
      source.connect(analyserNode);

      audioContextRef.current = audioContext;
      analyserRef.current = analyserNode;
      setAnalyser(analyserNode);

      setIsReady(true);
      setError(null);
      return true;
    } catch (err) {
      const message =
        err instanceof DOMException && err.name === 'NotAllowedError'
          ? 'Microphone access denied. Please allow microphone access in your browser settings.'
          : 'Failed to access microphone. Please check your device.';
      setError(message);
      return false;
    }
  }, []);

  const startRecording = useCallback(async () => {
    if (!mediaStreamRef.current) {
      const granted = await requestPermission();
      if (!granted) return;
    }

    setError(null);
    chunksRef.current = [];
    setDuration(0);

    const recorder = new MediaRecorder(mediaStreamRef.current!, {
      mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm',
    });

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };

    mediaRecorderRef.current = recorder;
    recorder.start(100); // Collect data every 100ms
    setIsRecording(true);

    // Duration tracking
    const startTime = Date.now();
    durationIntervalRef.current = setInterval(() => {
      setDuration((Date.now() - startTime) / 1000);
    }, 100);

    // Audio level monitoring
    levelIntervalRef.current = setInterval(() => {
      if (analyserRef.current) {
        const level = getAudioLevel(analyserRef.current);
        setAudioLevel(level);
      }
    }, 50);
  }, [requestPermission]);

  const stopRecording = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (!mediaRecorderRef.current || mediaRecorderRef.current.state !== 'recording') {
        resolve(null);
        return;
      }

      // Clear intervals
      if (durationIntervalRef.current) clearInterval(durationIntervalRef.current);
      if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);

      mediaRecorderRef.current.onstop = async () => {
        setIsRecording(false);
        setAudioLevel(0);

        // Convert recorded chunks to WAV
        const webmBlob = new Blob(chunksRef.current, { type: 'audio/webm' });

        try {
          // Decode the webm blob to AudioBuffer, then encode as WAV
          const arrayBuffer = await webmBlob.arrayBuffer();
          const audioContext = new AudioContext();
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
          const wavBlob = audioBufferToWav(audioBuffer);
          await audioContext.close();
          resolve(wavBlob);
        } catch {
          // Fallback: return the webm blob directly
          resolve(webmBlob);
        }
      };

      mediaRecorderRef.current.stop();
    });
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (durationIntervalRef.current) clearInterval(durationIntervalRef.current);
      if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
    };
  }, []);

  return {
    isRecording,
    isReady,
    audioLevel,
    duration,
    startRecording,
    stopRecording,
    error,
    requestPermission,
    analyser,
  };
}

"use client";

import type * as posedetection from '@tensorflow-models/pose-detection';

let tf: any;
let poseDetectionModule: typeof posedetection;

export interface AnalysisResult {
  pass: boolean;
  details: string[];
}

export interface SavadhanTelemetry {
  torso_posture: number;
  heel_alignment: number;
  foot_angle: number;
  arm_alignment: number;
  overall_score: number;
  isPoseDetected: boolean;
}

export default class PostureAnalyzer {
  private detector: posedetection.PoseDetector | null = null;
  private loadModelPromise: Promise<void> | null = null;
  private rules: any[]; // will be set to array of rule objects

  constructor(rules: any[]) {
    this.rules = rules;
  }

  // Load the MoveNet model (single pose) lazily
  private async loadModel() {
    if (!this.loadModelPromise) {
      this.loadModelPromise = (async () => {
        if (!poseDetectionModule) {
          tf = await import('@tensorflow/tfjs');
          await tf.ready(); // Ensure backend is fully initialized
          poseDetectionModule = await import('@tensorflow-models/pose-detection');
        }
        if (!this.detector) {
          try {
            const model = poseDetectionModule.SupportedModels.MoveNet;
            this.detector = await poseDetectionModule.createDetector(model, {
              modelType: 'SinglePose.Lightning',
            });
          } catch (err) {
            console.error("MoveNet load error:", err);
            this.loadModelPromise = null; // Allow retry
            throw err;
          }
        }
      })();
    }
    return this.loadModelPromise;
  }

  // Calculate distance between two keypoints
  private getDistance(p1: posedetection.Keypoint, p2: posedetection.Keypoint): number {
    return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
  }

  // Analyze a single frame and return continuous telemetry for Savadhan
  async predictFrame(frame: ImageData): Promise<SavadhanTelemetry> {
    await this.loadModel();
    if (!this.detector) throw new Error('Pose detector not initialized');

    const canvas = document.createElement('canvas');
    canvas.width = frame.width;
    canvas.height = frame.height;
    const ctx = canvas.getContext('2d');
    ctx?.putImageData(frame, 0, 0);
    
    const input = tf.browser.fromPixels(canvas);
    const poses = await this.detector.estimatePoses(input);
    tf.dispose(input);

    if (!poses || poses.length === 0) {
      return { torso_posture: 0, heel_alignment: 0, foot_angle: 0, arm_alignment: 0, overall_score: 0, isPoseDetected: false };
    }

    const kp = poses[0].keypoints;
    const keypoints = Object.fromEntries(kp.map((k: any) => [k.name, k]));

    // Savadhan Rules Logic:
    // 1. Heels together (distance between left_ankle and right_ankle should be minimal)
    let heel_alignment = 0;
    if (keypoints.left_ankle?.score > 0.3 && keypoints.right_ankle?.score > 0.3) {
      const dist = this.getDistance(keypoints.left_ankle, keypoints.right_ankle);
      // Normalized: 0 dist = 100%, 100px dist = 0%
      heel_alignment = Math.max(0, 100 - (dist / 1.5));
    }

    // 2. Arm alignment (wrists should be close to hips)
    let arm_alignment = 0;
    if (keypoints.left_wrist?.score > 0.3 && keypoints.left_hip?.score > 0.3 && 
        keypoints.right_wrist?.score > 0.3 && keypoints.right_hip?.score > 0.3) {
      const leftDist = this.getDistance(keypoints.left_wrist, keypoints.left_hip);
      const rightDist = this.getDistance(keypoints.right_wrist, keypoints.right_hip);
      const avgDist = (leftDist + rightDist) / 2;
      arm_alignment = Math.max(0, 100 - (avgDist / 1.5));
    }

    // 3. Torso posture (shoulders aligned horizontally, hips aligned horizontally, back straight)
    let torso_posture = 0;
    if (keypoints.left_shoulder?.score > 0.3 && keypoints.right_shoulder?.score > 0.3 &&
        keypoints.left_hip?.score > 0.3 && keypoints.right_hip?.score > 0.3) {
      const shoulderDiffY = Math.abs(keypoints.left_shoulder.y - keypoints.right_shoulder.y);
      const hipDiffY = Math.abs(keypoints.left_hip.y - keypoints.right_hip.y);
      torso_posture = Math.max(0, 100 - (shoulderDiffY + hipDiffY));
    }

    // 4. Foot angle (approximate 30 degrees using ankle to toe-end if available, else default to 90 for now)
    let foot_angle = 80; // Placeholder until detailed foot keypoints are used

    const overall_score = Math.round((heel_alignment + arm_alignment + torso_posture) / 3);

    return {
      torso_posture: Math.round(torso_posture),
      heel_alignment: Math.round(heel_alignment),
      foot_angle,
      arm_alignment: Math.round(arm_alignment),
      overall_score,
      isPoseDetected: true,
    };
  }

  // Analyze a set of ImageData frames and return pass/fail based on rules
  async analyze(frames: ImageData[]): Promise<AnalysisResult> {
    await this.loadModel();
    if (!this.detector) {
      throw new Error('Pose detector not initialized');
    }
    const violations: string[] = [];
    // Simple majority‑vote: if any frame violates a rule, count it.
    for (const frame of frames) {
      const canvas = document.createElement('canvas');
      canvas.width = frame.width;
      canvas.height = frame.height;
      const ctx = canvas.getContext('2d');
      ctx?.putImageData(frame, 0, 0);
      const input = tf.browser.fromPixels(canvas);
      const poses = await this.detector.estimatePoses(input);
      tf.dispose(input);
      if (poses && poses.length > 0) {
        const keypoints = poses[0].keypoints;
        // Evaluate each rule against the current keypoints
        for (const rule of this.rules) {
          const { name, condition } = rule;
          // condition is a JS expression string that can use keypoints, eg: "angle(keypoints[5], keypoints[7]) < 30"
          try {
            // eslint-disable-next-line no-new-func
            const fn = new Function('keypoints', 'angle', condition);
            const angle = (a: any, b: any, c: any) => {
              const toRad = (deg: number) => (deg * Math.PI) / 180;
              const ax = a.x - b.x;
              const ay = a.y - b.y;
              const cx = c.x - b.x;
              const cy = c.y - b.y;
              const dot = ax * cx + ay * cy;
              const magA = Math.sqrt(ax * ax + ay * ay);
              const magC = Math.sqrt(cx * cx + cy * cy);
              const cos = dot / (magA * magC);
              const deg = Math.acos(cos) * (180 / Math.PI);
              return deg;
            };
            const result = fn(keypoints, angle);
            if (!result) {
              violations.push(`${name} violated`);
            }
          } catch (e) {
            console.warn('Rule evaluation error', e);
          }
        }
      }
    }
    const pass = violations.length === 0;
    return { pass, details: violations };
  }
}

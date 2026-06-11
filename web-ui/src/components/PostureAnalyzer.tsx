"use client";

import type * as posedetection from '@tensorflow-models/pose-detection';

let tf: any;
let poseDetectionModule: typeof posedetection;

export interface AnalysisResult {
  pass: boolean;
  details: string[];
}

export interface DrillTelemetry {
  metrics: Record<string, number>;
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

  // Calculate angle at p2 (between p1-p2 and p3-p2)
  private getAngle(p1: posedetection.Keypoint, p2: posedetection.Keypoint, p3: posedetection.Keypoint): number {
    const v1 = { x: p1.x - p2.x, y: p1.y - p2.y };
    const v2 = { x: p3.x - p2.x, y: p3.y - p2.y };
    const dot = v1.x * v2.x + v1.y * v2.y;
    const mag1 = Math.sqrt(v1.x * v1.x + v1.y * v1.y);
    const mag2 = Math.sqrt(v2.x * v2.x + v2.y * v2.y);
    if (mag1 * mag2 === 0) return 0;
    return Math.acos(dot / (mag1 * mag2)) * (180 / Math.PI);
  }

  // Analyze a single frame and return continuous telemetry based on current drill
  async predictFrame(frame: ImageData, currentMode: string = "SAVDHAN"): Promise<DrillTelemetry> {
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
      return { metrics: {}, overall_score: 0, isPoseDetected: false };
    }

    const kp = poses[0].keypoints;
    
    // Ensure that at least 5 keypoints have a confidence score > 0.3.
    // If not, it means the camera is likely empty and MoveNet is just outputting noise.
    const confidentKeypoints = kp.filter((k: any) => k.score > 0.3);
    if (confidentKeypoints.length < 5) {
      return { metrics: {}, overall_score: 0, isPoseDetected: false };
    }

    const keypoints = Object.fromEntries(kp.map((k: any) => [k.name, k]));

    let metrics: Record<string, number> = {};
    let overall_score = 0;

    // Common: Torso Posture
    let torso_posture = 0;
    if (keypoints.left_shoulder?.score > 0.3 && keypoints.right_shoulder?.score > 0.3 &&
        keypoints.left_hip?.score > 0.3 && keypoints.right_hip?.score > 0.3) {
      const shoulderDiffY = Math.abs(keypoints.left_shoulder.y - keypoints.right_shoulder.y);
      const hipDiffY = Math.abs(keypoints.left_hip.y - keypoints.right_hip.y);
      const shoulderWidth = this.getDistance(keypoints.left_shoulder, keypoints.right_shoulder);
      if (shoulderWidth > 0) {
        // Less strict on minor vertical deviations (tolerance for loose clothing / minor tilt)
        torso_posture = Math.max(0, 100 - ((shoulderDiffY + hipDiffY) / shoulderWidth * 50));
      }
    }

    if (currentMode === "SAVDHAN") {
      // 1. Heels together
      let metricsCount = 0;
      let totalScore = 0;

      if (torso_posture > 0) {
        metrics["Torso Posture"] = Math.round(torso_posture);
        totalScore += torso_posture;
        metricsCount++;
      }

      if (keypoints.left_ankle?.score > 0.6 && keypoints.right_ankle?.score > 0.6) {
        if (keypoints.left_shoulder?.score > 0.3 && keypoints.right_shoulder?.score > 0.3) {
          const dist = this.getDistance(keypoints.left_ankle, keypoints.right_ankle);
          const shoulderWidth = this.getDistance(keypoints.left_shoulder, keypoints.right_shoulder);
          if (shoulderWidth > 0) {
            const normalized = dist / shoulderWidth;
            // Ankles will naturally have ~0.15-0.2 distance ratio even when heels touch
            const heel_alignment = Math.max(0, 100 - Math.max(0, normalized - 0.25) * 400);
            metrics["Heel Alignment"] = Math.round(heel_alignment);
            totalScore += heel_alignment;
            metricsCount++;
          }
        }
        // 2. Head Posture (Chin up, looking straight)
        if (keypoints.nose?.score > 0.6 && keypoints.left_shoulder?.score > 0.3 && keypoints.right_shoulder?.score > 0.3) {
          const shoulderMidX = (keypoints.left_shoulder.x + keypoints.right_shoulder.x) / 2;
          const noseDev = Math.abs(keypoints.nose.x - shoulderMidX);
          const shoulderWidth = this.getDistance(keypoints.left_shoulder, keypoints.right_shoulder);
          if (shoulderWidth > 0) {
            // Allow up to 10% deviation off-center without penalty
            const head_posture = Math.max(0, 100 - Math.max(0, (noseDev / shoulderWidth) - 0.1) * 300);
            metrics["Head Posture"] = Math.round(head_posture);
            totalScore += head_posture;
            metricsCount++;
          }
        }
        
        // 3. Knee Straightness (Ghutne kase hue)
        if (keypoints.left_hip?.score > 0.5 && keypoints.left_knee?.score > 0.5 && keypoints.left_ankle?.score > 0.5 &&
            keypoints.right_hip?.score > 0.5 && keypoints.right_knee?.score > 0.5 && keypoints.right_ankle?.score > 0.5) {
          const leftKneeAngle = this.getAngle(keypoints.left_hip, keypoints.left_knee, keypoints.left_ankle);
          const rightKneeAngle = this.getAngle(keypoints.right_hip, keypoints.right_knee, keypoints.right_ankle);
          // Ideal angle is 180 (straight), allow 10 degrees tolerance
          const leftStraight = Math.max(0, 100 - Math.max(0, Math.abs(180 - leftKneeAngle) - 10) * 5);
          const rightStraight = Math.max(0, 100 - Math.max(0, Math.abs(180 - rightKneeAngle) - 10) * 5);
          const knee_straightness = (leftStraight + rightStraight) / 2;
          metrics["Knee Straightness"] = Math.round(knee_straightness);
          totalScore += knee_straightness;
          metricsCount++;
        }
      }

      if (keypoints.left_wrist?.score > 0.5 && keypoints.left_hip?.score > 0.5 && 
          keypoints.right_wrist?.score > 0.5 && keypoints.right_hip?.score > 0.5 &&
          keypoints.left_shoulder?.score > 0.3) {
        const leftDist = this.getDistance(keypoints.left_wrist, keypoints.left_hip);
        const rightDist = this.getDistance(keypoints.right_wrist, keypoints.right_hip);
        const avgDist = (leftDist + rightDist) / 2;
        const torsoLength = this.getDistance(keypoints.left_shoulder, keypoints.left_hip);
        if (torsoLength > 0) {
          const normalized = avgDist / torsoLength;
          // Wrists and hips have natural separation due to body width, allow up to 0.25 ratio
          const arm_alignment = Math.max(0, 100 - Math.max(0, normalized - 0.25) * 300);
          metrics["Arm Alignment"] = Math.round(arm_alignment);
          totalScore += arm_alignment;
          metricsCount++;
        }
      }

      overall_score = metricsCount > 0 ? Math.round(totalScore / metricsCount) : 0;

    } else if (currentMode === "VISHRAM") {
      // 1. Feet apart (ideal distance approx shoulder width)
      let metricsCount = 0;
      let totalScore = 0;

      if (torso_posture > 0) {
        metrics["Torso Posture"] = Math.round(torso_posture);
        totalScore += torso_posture;
        metricsCount++;
      }

      if (keypoints.left_ankle?.score > 0.3 && keypoints.right_ankle?.score > 0.3 &&
          keypoints.left_shoulder?.score > 0.3 && keypoints.right_shoulder?.score > 0.3) {
        const ankleDist = this.getDistance(keypoints.left_ankle, keypoints.right_ankle);
        const shoulderDist = this.getDistance(keypoints.left_shoulder, keypoints.right_shoulder);
        if (shoulderDist > 0) {
          const ratio = ankleDist / shoulderDist;
          const diff = Math.abs(ratio - 1.2);
          const feet_distance_score = Math.max(0, 100 - (diff * 100));
          metrics["Feet Distance"] = Math.round(feet_distance_score);
          totalScore += feet_distance_score;
          metricsCount++;
        }
      }

      if (keypoints.left_wrist?.score > 0.3 && keypoints.right_wrist?.score > 0.3 &&
          keypoints.left_shoulder?.score > 0.3 && keypoints.right_shoulder?.score > 0.3) {
        const wristDist = this.getDistance(keypoints.left_wrist, keypoints.right_wrist);
        const shoulderDist = this.getDistance(keypoints.left_shoulder, keypoints.right_shoulder);
        if (shoulderDist > 0) {
          const ratio = wristDist / shoulderDist;
          const hands_behind_back = Math.max(0, 100 - (ratio * 150));
          metrics["Hands Clasped"] = Math.round(hands_behind_back);
          totalScore += hands_behind_back;
          metricsCount++;
        }
      }

      overall_score = metricsCount > 0 ? Math.round(totalScore / metricsCount) : 0;
    } else {
      // Generic fallback for other drills
      metrics = {
        "Torso Posture": Math.round(torso_posture)
      };
      overall_score = Math.round(torso_posture);
    }

    return {
      metrics,
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

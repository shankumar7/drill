import * as tf from '@tensorflow/tfjs';
import * as posedetection from '@tensorflow-models/pose-detection';

export interface AnalysisResult {
  pass: boolean;
  details: string[];
}

export default class PostureAnalyzer {
  private detector: posedetection.PoseDetector | null = null;
  private rules: any[]; // will be set to array of rule objects

  constructor(rules: any[]) {
    this.rules = rules;
  }

  // Load the MoveNet model (single pose) lazily
  private async loadModel() {
    if (!this.detector) {
      const model = posedetection.SupportedModels.MoveNet;
      this.detector = await posedetection.createDetector(model, {
        modelType: 'SinglePose.Lightning',
      });
    }
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

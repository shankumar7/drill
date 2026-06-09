export class CadetTracker {
  private activeCadetId: string = "CADET-01";
  private lastSeen: Record<string, number> = {}; // timestamp per camera ID

  constructor() {}

  public getCadetId(cameraId: string, isPoseDetected: boolean): string | null {
    const now = Date.now();
    
    if (isPoseDetected) {
      // If we see someone, update the last seen timestamp for this camera
      this.lastSeen[cameraId] = now;
      return this.activeCadetId;
    }

    // If no pose is detected on this camera, check if they were recently seen
    const lastSeenTime = this.lastSeen[cameraId] || 0;
    const timeSinceLastSeen = now - lastSeenTime;

    // Give a 2-second grace period for flickering or moving across cameras
    if (timeSinceLastSeen < 2000) {
      return this.activeCadetId;
    }

    // If we haven't seen them for > 2 seconds on this camera, return null (empty frame)
    return null;
  }
}

export const globalCadetTracker = new CadetTracker();

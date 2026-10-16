// The neural network finds 21 hand landmarks. These small, readable functions
// turn those landmarks into commands. Children can inspect the whole classifier.
export const LABELS = {attack: 'Атака', defend: 'Щит', heal: 'Лечение'};
const distance = (a, b) => Math.hypot(a.x-b.x, a.y-b.y, (a.z||0)-(b.z||0));

export function starterGesture(points) {
  if (!points || points.length !== 21) return null;
  const extended = [8, 12, 16, 20].map(tip =>
    distance(points[tip], points[0]) > distance(points[tip-2], points[0]) * 1.15);
  const [index, middle, ring, pinky] = extended;
  if (!index && !middle && !ring && !pinky) return 'attack';
  if (index && middle && ring && pinky) return 'defend';
  if (index && middle && !ring && !pinky) return 'heal';
  return null;
}

// Distances, rather than pixels: independent of image position and hand size.
export function features(points) {
  if (!points || points.length !== 21) return null;
  const scale = distance(points[0], points[9]);
  if (scale < .015) return null;
  const vector = [];
  for (const tip of [4, 8, 12, 16, 20]) {
    vector.push(distance(points[tip], points[0])/scale);
    vector.push(distance(points[tip], points[tip-2])/scale);
    vector.push(distance(points[tip], points[5])/scale);
    vector.push(distance(points[tip], points[17])/scale);
  }
  return vector;
}

export function classifyKNN(vector, samples) {
  if (!vector || !Object.keys(LABELS).every(label => samples.filter(s => s.label===label).length >= 5)) return null;
  const nearest = samples.map(s => ({label:s.label, distance:
    Math.sqrt(s.vector.reduce((sum, x, i)=>sum+(x-vector[i])**2,0)/vector.length)}))
    .sort((a,b)=>a.distance-b.distance).slice(0,3);
  if (nearest[0].distance > .35) return null; // unfamiliar gesture: abstain
  const votes = {};
  nearest.forEach(s => {votes[s.label]=(votes[s.label]||0)+1;});
  const [label, count] = Object.entries(votes).sort((a,b)=>b[1]-a[1])[0];
  return count >= 2 ? label : null;
}

// One action per presentation. A held fist must never keep attacking.
export class GestureLatch {
  constructor() { this.reset(); }
  reset() {this.candidate=null; this.since=0; this.fired=false; this.absentSince=null;}
  update(label, now) {
    if (!label) {
      this.candidate=null;
      if (this.absentSince===null) this.absentSince=now;
      if (now-this.absentSince>=500) this.fired=false;
      return null;
    }
    this.absentSince=null;
    if (label!==this.candidate) {this.candidate=label; this.since=now;}
    if (!this.fired && now-this.since>=650) {this.fired=true; return label;}
    return null;
  }
}

import './style.css';
import * as THREE from 'three';

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);

// Camera setup
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 4;

// Renderer setup
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

// Lighting
const pointLight = new THREE.PointLight(0xffffff, 1.2);
pointLight.position.set(2, 3, 4);
scene.add(pointLight);
const ambientLight = new THREE.AmbientLight(0x404040, 1.2);
scene.add(ambientLight);

// Dandelion stem
const stemCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, -2, 0),
  new THREE.Vector3(0.2, -1.5, 0),
  new THREE.Vector3(0.1, -0.5, 0),
  new THREE.Vector3(0, 0, 0)
]);

const stemGeometry = new THREE.TubeGeometry(stemCurve, 32, 0.03, 8, false);
const stemMaterial = new THREE.MeshPhongMaterial({ 
  color: 0x32CD32,
  shininess: 15
});
const stem = new THREE.Mesh(stemGeometry, stemMaterial);
scene.add(stem);

// Dandelion particles
const particleCount = 3000;
const particles = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);
const colors = new Float32Array(particleCount * 3);
const scales = new Float32Array(particleCount);
const velocities = new Float32Array(particleCount * 3);
const randomFactors = new Float32Array(particleCount);

for (let i = 0; i < particleCount; i++) {
  const phi = Math.random() * Math.PI * 2;
  const theta = Math.acos(2 * Math.random() - 1);
  const radius = 0.25;

  positions[i * 3] = radius * Math.sin(theta) * Math.cos(phi);
  positions[i * 3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
  positions[i * 3 + 2] = radius * Math.cos(theta);

  const baseSpeed = Math.random() * 0.03 + 0.02;
  velocities[i * 3] = Math.sin(theta) * Math.cos(phi) * baseSpeed * 2;
  velocities[i * 3 + 1] = Math.sin(theta) * Math.sin(phi) * baseSpeed * 2;
  velocities[i * 3 + 2] = baseSpeed * 6;

  const color = new THREE.Color(0xffffff);
  colors[i * 3] = color.r;
  colors[i * 3 + 1] = color.g;
  colors[i * 3 + 2] = color.b;

  scales[i] = Math.random() * 0.12 + 0.06;
  randomFactors[i] = Math.random() * 2 + 0.5;
}

particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
particles.setAttribute('color', new THREE.BufferAttribute(colors, 3));
particles.setAttribute('scale', new THREE.BufferAttribute(scales, 1));
particles.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
particles.setAttribute('randomFactor', new THREE.BufferAttribute(randomFactors, 1));

const particleMaterial = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 }
  },
  vertexShader: `
    attribute vec3 color;
    attribute float scale;
    attribute vec3 velocity;
    attribute float randomFactor;
    varying vec3 vColor;
    uniform float time;

    float rand(vec2 co) {
      return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
    }

    void main() {
      vColor = color;
      vec3 pos = position;
      
      float t = time * (1.0 + randomFactor * 0.5);
      vec3 movement = velocity * t;
      
      float windStrength = 0.05;
      float expansionFactor = min(t * 0.8, 1.2);
      movement.x += sin(t * 0.5 + pos.y) * windStrength * expansionFactor;
      movement.y += cos(t * 0.5 + pos.x) * windStrength * expansionFactor;
      movement.z += t * 1.2;
      
      pos += movement;
      
      vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
      gl_Position = projectionMatrix * mvPosition;
      gl_PointSize = scale * (400.0 / length(mvPosition.xyz));
    }
  `,
  fragmentShader: `
    varying vec3 vColor;

    void main() {
      float dist = length(gl_PointCoord - vec2(0.5));
      if (dist > 0.5) discard;
      float alpha = smoothstep(0.5, 0.0, dist);
      gl_FragColor = vec4(vColor, alpha * 0.6);
    }
  `,
  transparent: true,
  depthWrite: false,
  blending: THREE.AdditiveBlending
});

const particleSystem = new THREE.Points(particles, particleMaterial);
scene.add(particleSystem);

// Animation
let time = 0;

function animate() {
  requestAnimationFrame(animate);

  time += 0.01;
  particleMaterial.uniforms.time.value = time;
  
  stem.rotation.y = Math.sin(time * 0.2) * 0.08;
  renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});

// Start animation
animate();

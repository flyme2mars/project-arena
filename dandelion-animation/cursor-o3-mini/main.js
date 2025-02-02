/**
 * This file sets up a Three.js scene that simulates a realistic dandelion shedding its seeds,
 * with improved color contrast and a glow effect using post‑processing bloom.
 *
 * In this version:
 * - The background is set to black with matching fog.
 * - The dandelion head is built from round, textured particles in hot pink and white.
 * - A bloom pass adds a subtle glow to the dandelion head.
 * - The green stem is clearly visible.
 */

// Import Three.js using the import map, and load post-processing modules with full URLs.
import * as THREE from 'three'
import { EffectComposer } from 'https://cdn.jsdelivr.net/npm/three@0.150.1/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'https://cdn.jsdelivr.net/npm/three@0.150.1/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'https://cdn.jsdelivr.net/npm/three@0.150.1/examples/jsm/postprocessing/UnrealBloomPass.js'

// Global variables
let scene, camera, renderer, clock, composer
let dandelionParticles, dandelionMaterial, particleGeometry
let particleInitialPositions = []
let particleVelocities = []
let particleDelays = [] // Random delays (in seconds) before each seed detaches
const numParticles = 5000 // number of seeds/fluff
const dandelionRadius = 0.9 // radius of the dandelion head
const dispersionDistance = 2.0 // scale for displacement
const ANIM_DURATION = 5 // seconds for a seed's motion after detachment
let mistParticles

init()
animate()

/**
 * Creates a round particle texture using a canvas-based radial gradient.
 */
function createCircleTexture() {
  const size = 128
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const context = canvas.getContext('2d')

  const gradient = context.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
  gradient.addColorStop(0, 'rgba(255,255,255,1.0)') // center is white
  gradient.addColorStop(0.4, 'rgba(255,255,255,0.8)')
  gradient.addColorStop(1, 'rgba(255,255,255,0.0)') // edge is transparent
  context.fillStyle = gradient
  context.fillRect(0, 0, size, size)

  return new THREE.CanvasTexture(canvas)
}

function init() {
  // Create the scene with a black background and matching fog.
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x000000)
  scene.fog = new THREE.FogExp2(0x000000, 0.3)

  // Set up the camera.
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100)
  camera.position.z = 5

  // Set up the renderer.
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(window.innerWidth, window.innerHeight)
  document.body.appendChild(renderer.domElement)

  // Set up post-processing (bloom for glow).
  composer = new EffectComposer(renderer)
  composer.addPass(new RenderPass(scene, camera))
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.8, // strength
    0.4, // radius
    0.1 // threshold
  )
  composer.addPass(bloomPass)

  // Clock for animation timing.
  clock = new THREE.Clock()

  // Add lights.
  const pointLight = new THREE.PointLight(0xffffff, 1, 100)
  pointLight.position.set(0, 0, 3)
  scene.add(pointLight)
  scene.add(new THREE.AmbientLight(0x555555))

  // Create a round particle texture.
  const particleTexture = createCircleTexture()

  // Create the particle geometry for the dandelion head.
  particleGeometry = new THREE.BufferGeometry()
  const positions = new Float32Array(numParticles * 3)
  const colors = new Float32Array(numParticles * 3)

  // For each seed:
  // - Pick a random point on a sphere,
  // - Save its initial position,
  // - Compute an outward velocity with a slight wind bias,
  // - Set a random delay for detachment,
  // - Assign a color (hot pink or white).
  for (let i = 0; i < numParticles; i++) {
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(THREE.MathUtils.randFloatSpread(2))
    const x = dandelionRadius * Math.sin(phi) * Math.cos(theta)
    const y = dandelionRadius * Math.sin(phi) * Math.sin(theta)
    const z = dandelionRadius * Math.cos(phi)

    positions[i * 3] = x
    positions[i * 3 + 1] = y
    positions[i * 3 + 2] = z
    particleInitialPositions.push(new THREE.Vector3(x, y, z))

    let v = new THREE.Vector3(x, y, z).normalize()
    v.add(new THREE.Vector3(0.3, 0.0, 0.0)) // wind bias in +X
    v.normalize()
    const speed = THREE.MathUtils.randFloat(1.5, 2.5)
    v.multiplyScalar(speed)
    particleVelocities.push(v)

    // Each seed detaches after a random delay (0 to 2 seconds).
    particleDelays.push(Math.random() * 2.0)

    // Use hot pink (#FF69B4) or white.
    if (Math.random() < 0.5) {
      // Hot pink: rgb(255,105,180) normalized.
      colors[i * 3] = 1.0
      colors[i * 3 + 1] = 105 / 255
      colors[i * 3 + 2] = 180 / 255
    } else {
      colors[i * 3] = 1.0
      colors[i * 3 + 1] = 1.0
      colors[i * 3 + 2] = 1.0
    }
  }
  particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  // Create the Points material for the dandelion head.
  dandelionMaterial = new THREE.PointsMaterial({
    map: particleTexture,
    size: 0.08,
    vertexColors: true,
    transparent: true,
    opacity: 1.0,
    alphaTest: 0.05,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true,
  })

  // Create and position the particle system.
  dandelionParticles = new THREE.Points(particleGeometry, dandelionMaterial)
  dandelionParticles.position.set(0, 0.5, 0)
  dandelionParticles.renderOrder = 0 // Render before the stem.
  scene.add(dandelionParticles)

  // Create the green stem using TubeGeometry along a quadratic Bezier curve.
  const stemCurve = new THREE.QuadraticBezierCurve3(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0.5, -1.5, 0), new THREE.Vector3(0, -3, 0))
  // Use a thicker tube (0.1 radius) for a more visible stem.
  const stemGeometry = new THREE.TubeGeometry(stemCurve, 20, 0.1, 8, false)
  const stemMaterial = new THREE.MeshStandardMaterial({
    color: 0x228b22,
    emissive: 0x114411,
    emissiveIntensity: 0.7,
    side: THREE.DoubleSide,
  })
  const stemMesh = new THREE.Mesh(stemGeometry, stemMaterial)
  // Position the stem so its top aligns with the dandelion head,
  // and shift it along the Z-axis for visibility.
  stemMesh.position.set(0, 0.5, 0.3)
  stemMesh.renderOrder = 1 // Render after the particles.
  scene.add(stemMesh)
  scene.userData.stemMesh = stemMesh

  // Create a faint mist/dust background using another particle system.
  const mistCount = 300
  const mistGeometry = new THREE.BufferGeometry()
  const mistPositions = new Float32Array(mistCount * 3)
  for (let i = 0; i < mistCount; i++) {
    mistPositions[i * 3] = THREE.MathUtils.randFloatSpread(10)
    mistPositions[i * 3 + 1] = THREE.MathUtils.randFloatSpread(10)
    mistPositions[i * 3 + 2] = THREE.MathUtils.randFloatSpread(10)
  }
  mistGeometry.setAttribute('position', new THREE.BufferAttribute(mistPositions, 3))
  const mistMaterial = new THREE.PointsMaterial({
    map: particleTexture,
    size: 0.1,
    color: 0xffffff,
    transparent: true,
    opacity: 0.05,
    alphaTest: 0.05,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true,
  })
  mistParticles = new THREE.Points(mistGeometry, mistMaterial)
  scene.add(mistParticles)

  // Adjust the scene if the window resizes.
  window.addEventListener('resize', onWindowResize)
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
  composer.setSize(window.innerWidth, window.innerHeight)
}

/**
 * In the animate loop:
 * - For each seed, before its detachment delay, it stays in place.
 * - After detachment, its new position is computed (using an ease-out function, wind, and jitter).
 * - The stem gently sways.
 * - Rendering is performed via the composer so that the bloom effect applies.
 */
function animate() {
  requestAnimationFrame(animate)
  const elapsed = clock.getElapsedTime()
  const positions = particleGeometry.attributes.position.array

  for (let i = 0; i < numParticles; i++) {
    const initPos = particleInitialPositions[i]
    const delay = particleDelays[i]
    const baseIndex = i * 3
    if (elapsed < delay) {
      positions[baseIndex] = initPos.x
      positions[baseIndex + 1] = initPos.y
      positions[baseIndex + 2] = initPos.z
    } else {
      const dt = elapsed - delay
      const progress = Math.min(dt / ANIM_DURATION, 1)
      const ease = progress * (2 - progress) // ease-out quadratic
      const displacement = particleVelocities[i].clone().multiplyScalar(dispersionDistance * ease)
      const windEffect = new THREE.Vector3(0.5 * dt, 0.1 * Math.sin(elapsed + i), 0)
      const jitter = new THREE.Vector3(0.01 * Math.sin(elapsed * 3 + i), 0.01 * Math.cos(elapsed * 3 + i), 0.01 * Math.sin(elapsed * 2 + i))
      const newPos = initPos.clone().add(displacement).add(windEffect).add(jitter)
      positions[baseIndex] = newPos.x
      positions[baseIndex + 1] = newPos.y
      positions[baseIndex + 2] = newPos.z
    }
  }
  particleGeometry.attributes.position.needsUpdate = true

  // Animate the stem with a gentle sway.
  const stemMesh = scene.userData.stemMesh
  if (stemMesh) {
    stemMesh.rotation.z = 0.05 * Math.sin(elapsed * 2)
  }

  // Render the scene with bloom.
  composer.render()
}

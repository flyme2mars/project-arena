import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { gsap } from 'gsap';
import styled from 'styled-components';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';

const CanvasContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
`;

const ThreeScene = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const composerRef = useRef<EffectComposer | null>(null);
  const particlesRef = useRef<THREE.Points | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    sceneRef.current = new THREE.Scene();
    cameraRef.current = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    rendererRef.current = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    rendererRef.current.setSize(window.innerWidth, window.innerHeight);
    containerRef.current.appendChild(rendererRef.current.domElement);

    // Create city geometry
    const cityGeometry = new THREE.BoxGeometry(0.3, 1, 0.3);
    const cityMaterial = new THREE.MeshPhongMaterial({
      color: 0x00ff88,
      wireframe: true,
      wireframeLinewidth: 1.5,
    });

    // Create city buildings
    const buildings = new THREE.Group();
    for(let i = 0; i < 50; i++) {
      const height = Math.random() * 2 + 0.5;
      const building = new THREE.Mesh(
        new THREE.BoxGeometry(0.3, height, 0.3),
        cityMaterial
      );
      building.position.x = Math.random() * 10 - 5;
      building.position.z = Math.random() * 10 - 5;
      building.position.y = height/2;
      buildings.add(building);
    }
    sceneRef.current.add(buildings);

    // Create particles
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 5000;
    const posArray = new Float32Array(particlesCount * 3);
    
    for(let i = 0; i < particlesCount * 3; i++) {
      posArray[i] = (Math.random() - 0.5) * 15;
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    
    const particlesMaterial = new THREE.PointsMaterial({
      size: 0.005,
      color: 0x00ffaa,
      blending: THREE.AdditiveBlending,
      transparent: true
    });
    
    particlesRef.current = new THREE.Points(particlesGeometry, particlesMaterial);
    sceneRef.current.add(particlesRef.current);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    const pointLight = new THREE.PointLight(0xffffff, 1);
    pointLight.position.set(10, 10, 10);
    sceneRef.current.add(ambientLight, pointLight);

    // Position camera
    cameraRef.current.position.z = 8;
    cameraRef.current.position.y = 3;
    cameraRef.current.lookAt(0, 0, 0);

    // Setup post-processing
    composerRef.current = new EffectComposer(rendererRef.current);
    const renderPass = new RenderPass(sceneRef.current, cameraRef.current);
    composerRef.current.addPass(renderPass);

    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(window.innerWidth, window.innerHeight),
      1.5, // strength
      0.4, // radius
      0.85 // threshold
    );
    composerRef.current.addPass(bloomPass);

    // Animation
    const animate = () => {
      if (!sceneRef.current || !cameraRef.current || !composerRef.current || !particlesRef.current) return;

      requestAnimationFrame(animate);
      
      // Animate particles
      particlesRef.current.rotation.y += 0.0005;
      particlesRef.current.rotation.x += 0.0002;

      // Move camera based on mouse position
      const targetX = (mousePosition.x * 0.01 - cameraRef.current.position.x) * 0.05;
      const targetY = (mousePosition.y * 0.01 - cameraRef.current.position.y) * 0.05;
      cameraRef.current.position.x += targetX;
      cameraRef.current.position.y += targetY;
      cameraRef.current.lookAt(0, 0, 0);

      // Render with post-processing
      composerRef.current.render();
    };

    // Handle mouse movement
    const handleMouseMove = (event: MouseEvent) => {
      setMousePosition({
        x: event.clientX - window.innerWidth / 2,
        y: -(event.clientY - window.innerHeight / 2)
      });
    };

    window.addEventListener('mousemove', handleMouseMove);

    // GSAP animations for buildings
    buildings.children.forEach((building, index) => {
      gsap.to(building.scale, {
        y: 1.5,
        duration: 2 + Math.random() * 2,
        repeat: -1,
        yoyo: true,
        ease: "power2.inOut",
        delay: index * 0.1
      });
    });

    animate();

    // Handle resize
    const handleResize = () => {
      if (!cameraRef.current || !rendererRef.current) return;
      
      cameraRef.current.aspect = window.innerWidth / window.innerHeight;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      containerRef.current?.removeChild(rendererRef.current!.domElement);
    };
  }, []);

  return <CanvasContainer ref={containerRef} />;
};

export default ThreeScene;
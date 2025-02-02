import { useEffect, useRef } from 'react';
import styled from 'styled-components';
import { gsap } from 'gsap';
import ThreeScene from './components/ThreeScene';

const Container = styled.div`
  min-height: 100vh;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.4) 100%);
  backdrop-filter: blur(5px);
`;

const Title = styled.h1`
  font-size: clamp(3rem, 8vw, 8rem);
  font-weight: 900;
  margin: 0;
  opacity: 0;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  background: linear-gradient(120deg, #00ff88, #00ffaa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 2rem rgba(0,255,136,0.3));
  transform: translateY(50px);
`;

const Subtitle = styled.p`
  font-size: clamp(1rem, 2vw, 1.5rem);
  margin-top: 1rem;
  opacity: 0;
  max-width: 600px;
  text-align: center;
  line-height: 1.6;
  color: rgba(255,255,255,0.8);
  transform: translateY(30px);
  text-shadow: 0 0 20px rgba(0,255,136,0.2);
`;

const Button = styled.button`
  background: transparent;
  border: 2px solid #00ff88;
  color: #00ff88;
  padding: 1.2rem 3rem;
  font-size: 1.1rem;
  margin-top: 3rem;
  cursor: pointer;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
  z-index: 1;

  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 0;
    height: 100%;
    background: #00ff88;
    transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: -1;
  }

  &:hover {
    color: black;
    &:before {
      width: 100%;
    }
  }
`;

function App() {
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const timeline = gsap.timeline({ defaults: { ease: 'power3.out' } });

    timeline
      .to(titleRef.current, { opacity: 1, y: 0, duration: 1, delay: 0.5 })
      .to(subtitleRef.current, { opacity: 1, y: 0, duration: 1 }, '-=0.5')
      .to(buttonRef.current, { opacity: 1, y: 0, duration: 1 }, '-=0.5');
  }, []);

  return (
    <>
      <ThreeScene />
      <Container>
        <Title ref={titleRef}>Digital Artistry</Title>
        <Subtitle ref={subtitleRef}>
          Pushing the boundaries of web design through innovative interactions
          and immersive experiences.
        </Subtitle>
        <Button ref={buttonRef}>Explore</Button>
      </Container>
    </>
  );
}

export default App;

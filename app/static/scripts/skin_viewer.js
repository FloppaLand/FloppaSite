import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { remapUVs } from './skin_geometry.js';

let scene, camera, renderer, controls;
let modelGroup, leftArm, rightArm, leftLeg, rightLeg;
let currentMaterial = null;

let isWalking = true;
let isRotating = true;
let clock = new THREE.Clock();


export function initViewer(containerId, initialSkinUrl) {
    const container = document.getElementById(containerId);

    scene = new THREE.Scene();


    camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);
    camera.position.set(0, 0, 45);


    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    container.appendChild(renderer.domElement);


    scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.5);
    keyLight.position.set(10, 10, 10);
    scene.add(keyLight);
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.8);
    fillLight.position.set(-10, 5, 10);
    scene.add(fillLight);


    controls = new OrbitControls(camera, renderer.domElement);
    controls.enablePan = false;
    controls.enableZoom = false;
    controls.minDistance = 20;
    controls.maxDistance = 80;


    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            const width = entry.contentRect.width;
            const height = entry.contentRect.height;
            
            renderer.setSize(width, height);
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
        }
    });
    resizeObserver.observe(container);

    loadSkin(initialSkinUrl);

    animate();
}

function createSkinPart(w, h, d, texX, texY, material, isOuter = false) {
    const inflation = isOuter ? 0.25 : 0;
    const geometry = new THREE.BoxGeometry(w + inflation*2, h + inflation*2, d + inflation*2);
    remapUVs(geometry, texX, texY, w, h, d);
    return new THREE.Mesh(geometry, material);
}

function loadSkin(url) {
    const loader = new THREE.TextureLoader();
    loader.setCrossOrigin('anonymous');
    
    loader.load(url, (texture) => {
        texture.magFilter = THREE.NearestFilter; 
        texture.minFilter = THREE.NearestFilter;
        texture.colorSpace = THREE.SRGBColorSpace;

        if (currentMaterial) currentMaterial.dispose();
        
        currentMaterial = new THREE.MeshStandardMaterial({
            map: texture,
            transparent: true,
            alphaTest: 0.5,
            side: THREE.DoubleSide,
            roughness: 1,
            metalness: 0
        });

        buildModel();
    });
}

function buildModel() {
    if (modelGroup) scene.remove(modelGroup);

    modelGroup = new THREE.Group();
    modelGroup.position.y = -2;

    const armWidth = 4; // Steve
    const armOffset = 6;

    // -- HEAD --
    const headGroup = new THREE.Group();
    headGroup.position.set(0, 10, 0);
    const headInner = createSkinPart(8, 8, 8, 0, 0, currentMaterial);
    headInner.position.set(0, 4, 0);
    const headOuter = createSkinPart(8, 8, 8, 32, 0, currentMaterial, true);
    headOuter.position.set(0, 4, 0);
    headGroup.add(headInner, headOuter);
    modelGroup.add(headGroup);


    const bodyGroup = new THREE.Group();
    bodyGroup.position.set(0, 4, 0);
    bodyGroup.add(createSkinPart(8, 12, 4, 16, 16, currentMaterial));
    bodyGroup.add(createSkinPart(8, 12, 4, 16, 32, currentMaterial, true)); 
    modelGroup.add(bodyGroup);

    // -- RIGHT ARM --
    rightArm = new THREE.Group();
    rightArm.position.set(-armOffset, 8, 0);
    const rArmPivot = new THREE.Group();
    rArmPivot.position.set(0, -4, 0); 
    rArmPivot.add(createSkinPart(armWidth, 12, 4, 40, 16, currentMaterial));
    rArmPivot.add(createSkinPart(armWidth, 12, 4, 40, 32, currentMaterial, true));
    rightArm.add(rArmPivot);
    modelGroup.add(rightArm);

    // -- LEFT ARM --
    leftArm = new THREE.Group();
    leftArm.position.set(armOffset, 8, 0);
    const lArmPivot = new THREE.Group();
    lArmPivot.position.set(0, -4, 0);
    lArmPivot.add(createSkinPart(armWidth, 12, 4, 32, 48, currentMaterial));
    lArmPivot.add(createSkinPart(armWidth, 12, 4, 48, 48, currentMaterial, true));
    leftArm.add(lArmPivot);
    modelGroup.add(leftArm);

    // -- RIGHT LEG --
    rightLeg = new THREE.Group();
    rightLeg.position.set(-1.9, -2, 0);
    const rLegPivot = new THREE.Group();
    rLegPivot.position.set(0, -6, 0);
    rLegPivot.add(createSkinPart(4, 12, 4, 0, 16, currentMaterial));
    rLegPivot.add(createSkinPart(4, 12, 4, 0, 32, currentMaterial, true));
    rightLeg.add(rLegPivot);
    modelGroup.add(rightLeg);

    // -- LEFT LEG --
    leftLeg = new THREE.Group();
    leftLeg.position.set(1.9, -2, 0);
    const lLegPivot = new THREE.Group();
    lLegPivot.position.set(0, -6, 0);
    lLegPivot.add(createSkinPart(4, 12, 4, 16, 48, currentMaterial));
    lLegPivot.add(createSkinPart(4, 12, 4, 0, 48, currentMaterial, true));
    leftLeg.add(lLegPivot);
    modelGroup.add(leftLeg);

    scene.add(modelGroup);
}


export function toggleWalk(val) { isWalking = val; }
export function toggleRotate(val) { isRotating = val; }

function animate() {
    requestAnimationFrame(animate);

    controls.autoRotate = isRotating;
    if(isRotating) controls.autoRotateSpeed = 4;
    controls.update();

    if (modelGroup) {
        if (isWalking) {
            const time = clock.getElapsedTime() * 3;
            leftArm.rotation.x = Math.sin(time) * 0.6;
            rightArm.rotation.x = -Math.sin(time) * 0.6;
            leftLeg.rotation.x = -Math.sin(time) * 0.4;
            rightLeg.rotation.x = Math.sin(time) * 0.4;
            modelGroup.position.y = Math.sin(time * 2) * 0.2 - 2;
        } else {
            leftArm.rotation.x = 0; rightArm.rotation.x = 0;
            leftLeg.rotation.x = 0; rightLeg.rotation.x = 0;
            modelGroup.position.y = -2;
        }
    }

    renderer.render(scene, camera);
}
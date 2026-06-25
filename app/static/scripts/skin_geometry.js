// Перераспределение UV-координат под стандарт скинов Minecraft
export function remapUVs(geometry, texX, texY, w, h, d) {
    const texWidth = 64;
    const texHeight = 64;

    const u0 = texX;
    const v0 = texY;

    const toUV = (x, y) => ({
        x: x / texWidth,
        y: 1 - (y / texHeight)
    });

    const right = { x: u0, y: v0 + d, w: d, h: h };
    const front = { x: u0 + d, y: v0 + d, w: w, h: h };
    const left = { x: u0 + d + w, y: v0 + d, w: d, h: h };
    const back = { x: u0 + d + w + d, y: v0 + d, w: w, h: h };
    const top = { x: u0 + d, y: v0, w: w, h: d };
    const bottom = { x: u0 + d + w, y: v0, w: w, h: d };

    const uvAttribute = geometry.attributes.uv;

    const setFace = (faceIndex, rect) => {
        const tl = toUV(rect.x, rect.y);
        const tr = toUV(rect.x + rect.w, rect.y);
        const bl = toUV(rect.x, rect.y + rect.h);
        const br = toUV(rect.x + rect.w, rect.y + rect.h);

        const offset = faceIndex * 4;
        uvAttribute.setXY(offset + 0, tl.x, tl.y);
        uvAttribute.setXY(offset + 1, tr.x, tr.y);
        uvAttribute.setXY(offset + 2, bl.x, bl.y);
        uvAttribute.setXY(offset + 3, br.x, br.y);
    };

    setFace(0, left);   // Left
    setFace(1, right);  // Right
    setFace(2, top);    // Top
    setFace(3, bottom); // Bottom
    setFace(4, front);  // Front
    setFace(5, back);   // Back

    uvAttribute.needsUpdate = true;
}
        {
          // Optional viewer controls: color legend and frame player.
          // Injected after ``scene.add(gltf.scene);`` only when viewer data is given.
          const d = ansysViewerData;
          const panelStyle = "position:fixed;padding:8px 12px;border-radius:8px;"
            + "background:rgba(20,22,26,0.78);border:1px solid rgba(124,215,255,0.2);"
            + "font-size:13px;backdrop-filter:blur(8px);";

          if (d.legend) {
            const legend = document.createElement("div");
            legend.id = "ansys-legend";
            legend.style.cssText = panelStyle + "top:12px;right:12px;";
            const title = document.createElement("div");
            title.textContent = d.legend.title || "";
            const stops = [];
            for (let i = 0; i < 256; i += 15) {
              stops.push("rgb(" + d.lut.slice(3 * i, 3 * i + 3).join(",") + ")");
            }
            const bar = document.createElement("div");
            bar.style.cssText = "width:200px;height:12px;margin:4px 0;"
              + "background:linear-gradient(to right," + stops.join(",") + ")";
            const range = document.createElement("div");
            range.style.cssText = "display:flex;justify-content:space-between";
            const lo = document.createElement("span");
            const hi = document.createElement("span");
            lo.textContent = Number(d.legend.vmin).toPrecision(3);
            hi.textContent = Number(d.legend.vmax).toPrecision(3);
            range.append(lo, hi);
            legend.append(title, bar, range);
            document.body.append(legend);
          }

          if (d.frames) {
            const f = d.frames;
            const levels = Uint8Array.from(atob(f.data), (c) => c.charCodeAt(0));
            const nFrames = f.times.length;
            const nVerts = levels.length / nFrames;
            let colors = null;
            gltf.scene.traverse((obj) => {
              const attr = obj.isMesh && obj.geometry.getAttribute("color");
              if (attr && attr.count === nVerts) {
                colors = attr;
                // Matte surface so the field colors read clearly.
                obj.material.metalness = 0;
              }
            });
            if (!colors) {
              console.warn("Viewer controls: no mesh with " + nVerts + " vertex colors found.");
            }
            // The lookup table is sRGB; vertex colors are linear.
            const lut = [];
            for (let i = 0; i < 256; i++) {
              const c = new THREE.Color().setRGB(
                d.lut[3 * i] / 255, d.lut[3 * i + 1] / 255, d.lut[3 * i + 2] / 255,
                THREE.SRGBColorSpace);
              lut.push(c.r, c.g, c.b);
            }

            const player = document.createElement("div");
            player.id = "ansys-player";
            player.style.cssText = panelStyle + "bottom:16px;left:50%;"
              + "transform:translateX(-50%);display:flex;gap:10px;align-items:center;";
            const play = document.createElement("button");
            play.type = "button";
            const slider = Object.assign(document.createElement("input"),
              { type: "range", min: 0, max: nFrames - 1, value: 0 });
            slider.style.width = "40vw";
            const label = document.createElement("span");
            player.append(play, slider, label);
            document.body.append(player);

            const timeLabel = f.label || "Time";
            const show = (k) => {
              if (colors) {
                for (let i = 0; i < nVerts; i++) {
                  const j = 3 * levels[k * nVerts + i];
                  colors.setXYZ(i, lut[j], lut[j + 1], lut[j + 2]);
                }
                colors.needsUpdate = true;
              }
              slider.value = k;
              label.textContent = timeLabel + " " + f.times[k];
            };
            let timer = null;
            const stop = () => { clearInterval(timer); timer = null; play.textContent = "Play"; };
            play.onclick = () => {
              if (timer) return stop();
              play.textContent = "Pause";
              timer = setInterval(() => show((+slider.value + 1) % nFrames), 1000 / (f.fps || 20));
            };
            slider.oninput = () => { stop(); show(+slider.value); };
            stop();
            show(0);
          }
        }

document.addEventListener("DOMContentLoaded", () => {
    // находим все блоки .group и выбираем тот, где заголовок "Вход"
    const enter_group = Array.from(document.querySelectorAll(".group")).find(g => {
        const h4 = g.querySelector("h4");
        return h4 && h4.textContent.trim() === "Вход";
    });

    if (!enter_group) return; // если блока нет — выходим

    const enter_imgs = enter_group.querySelectorAll(".row img");
    const enter_cameras_id = [];
    const enter_cameras_time = [];

    const enter_socket = new WebSocket('ws://' + window.location.host + '/enter/-1');

    enter_socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        let idx = enter_cameras_id.indexOf(data.id);

        // если камеры ещё нет в массиве
        if (idx === -1) {
            enter_cameras_id.push(data.id);
            const now = new Date();
            enter_cameras_time.push([now.getMinutes(), now.getSeconds()]);

            // вставляем изображение в первый пустой img
            const img_elem = enter_imgs[enter_cameras_id.length - 1];
            if (img_elem) {
                img_elem.src = "data:image/jpeg;base64," + data.image;
            }
            console.log("ADDED", data.id);
        } else {
            const now = new Date();
            enter_cameras_time[idx] = [now.getMinutes(), now.getSeconds()];

            const img_elem = enter_imgs[idx];
            if (img_elem) {
                img_elem.src = "data:image/jpeg;base64," + data.image;
            }
        }

        console.log(enter_cameras_id);
    };

    // проверка времени для замены на "not_found"
    setInterval(() => {
        const now = new Date();
        enter_imgs.forEach((img, i) => {
            const cam_id = enter_cameras_id[i];
            const last_time = enter_cameras_time[i];
            if (!cam_id || !last_time) return;

            if (now.getMinutes() - last_time[0] > 0 || now.getSeconds() - last_time[1] > 6) {
                img.src = "/media/not_found.png";
            }
        });
    }, 1000);
});

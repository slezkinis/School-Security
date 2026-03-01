document.addEventListener("DOMContentLoaded", () => {
    // находим блок .group с заголовком "Выход"
    const exit_group = Array.from(document.querySelectorAll(".group")).find(g => {
        const h4 = g.querySelector("h4");
        return h4 && h4.textContent.trim() === "Выход";
    });

    if (!exit_group) return; // если блока нет — выходим

    const exit_imgs = exit_group.querySelectorAll(".row img");
    const exit_cameras_id = [];
    const exit_cameras_time = [];

    const exit_socket = new WebSocket('ws://' + window.location.host + '/exit/-1');

    exit_socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        let idx = exit_cameras_id.indexOf(data.id);

        // если камеры ещё нет в массиве
        if (idx === -1) {
            exit_cameras_id.push(data.id);
            const now = new Date();
            exit_cameras_time.push([now.getMinutes(), now.getSeconds()]);

            // вставляем изображение в первый пустой img
            const img_elem = exit_imgs[exit_cameras_id.length - 1];
            if (img_elem) {
                img_elem.src = "data:image/jpeg;base64," + data.image;
            }
            console.log("ADDED", data.id);
        } else {
            const now = new Date();
            exit_cameras_time[idx] = [now.getMinutes(), now.getSeconds()];

            const img_elem = exit_imgs[idx];
            if (img_elem) {
                img_elem.src = "data:image/jpeg;base64," + data.image;
            }
        }

        console.log(exit_cameras_id);
    };

    // проверка времени для замены на "not_found"
    setInterval(() => {
        const now = new Date();
        exit_imgs.forEach((img, i) => {
            const cam_id = exit_cameras_id[i];
            const last_time = exit_cameras_time[i];
            if (!cam_id || !last_time) return;

            if (now.getMinutes() - last_time[0] > 0 || now.getSeconds() - last_time[1] > 6) {
                img.src = "/media/not_found.png";
            }
        });
    }, 1000);
});

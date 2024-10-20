let enter_div = document.querySelector(".enter")
let enter_cameras_id = [];
let enter_cameras_time = [];
const enter_socket = new WebSocket(
    'ws://' +
    window.location.host +
    '/enter/-1'
)
enter_socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    var idx = enter_cameras_id.indexOf(data["id"])
    if (idx == -1) {
        enter_cameras_id.push(data["id"])
        Data = new Date();
        enter_cameras_time.push([Data.getMinutes(), Data.getSeconds()])
        document.querySelector(`#enter_${data["id"]}`).querySelector("img").src = "data:image/jpeg;base64, " + data["image"]
        console.log("ADDED")
    } else {
        Data = new Date();
        enter_cameras_time[enter_cameras_id.indexOf(data["id"])] = [Data.getMinutes(), Data.getSeconds()]
        document.querySelector(`#enter_${data["id"]}`).querySelector("img").src = "data:image/jpeg;base64, " + data["image"]
    }
    console.log(enter_cameras_id)
}

function check_time() {
    Data = new Date();
    enter_div.querySelectorAll(".video-item").forEach(item => {
        let my_id = item.id.replace("enter_", "");
        if (enter_cameras_id.indexOf(my_id) != -1) {
            let last_time = enter_cameras_time[enter_cameras_id.indexOf(my_id)]
            if (Data.getMinutes() - last_time[0] > 0 || Data.getSeconds() - last_time[1] > 6) {
                let img_camera = item.querySelector("img")
                img_camera.src = "/media/not_found.png"
            }
        }
})
}
setInterval(check_time, 10)
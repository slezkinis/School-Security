let exit_div = document.querySelector(".exit")
let exit_cameras_id = [];
let exit_cameras_time = [];
const exit_socket = new WebSocket(
    'ws://' +
    window.location.host +
    '/exit/-1'
)
exit_socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    var idx = exit_cameras_id.indexOf(data["id"])
    if (idx == -1) {
        exit_cameras_id.push(data["id"])
        Data = new Date();
        exit_cameras_time.push([Data.getMinutes(), Data.getSeconds()])
        document.querySelector(`#exit_${data["id"]}`).querySelector("img").src = "data:image/jpeg;base64, " + data["image"]
        console.log("ADDED")
    } else {
        Data = new Date();
        exit_cameras_time[exit_cameras_id.indexOf(data["id"])] = [Data.getMinutes(), Data.getSeconds()]
        document.querySelector(`#exit_${data["id"]}`).querySelector("img").src = "data:image/jpeg;base64, " + data["image"]
    }
    console.log(exit_cameras_id)
}

function check_time() {
    Data = new Date();
    exit_div.querySelectorAll(".video-item").forEach(item => {
        let my_id = item.id.replace("exit_", "");
        if (exit_cameras_id.indexOf(my_id) != -1) {
            let last_time = exit_cameras_time[exit_cameras_id.indexOf(my_id)]
            if (Data.getMinutes() - last_time[0] > 0 || Data.getSeconds() - last_time[1] > 1) {
                let img_camera = item.querySelector("img")
                img_camera.src = "/media/not_found.png"
            }
        }
})
}
setInterval(check_time, 10)
let enter_div = document.querySelector(".enter")
let exit_div = document.querySelector(".exit")
console.log(enter_div)
console.log(exit_div)
let enter_cameras_id = [];
let enter_cameras_time = [];
// console.log(camera_div)
const enter_socket = new WebSocket(
    'ws://' +
    window.location.host +
    '/enter/-1'
)
enter_socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    // console.log(data)
    var idx = enter_cameras_id.indexOf(data["id"])
    if (idx == -1) {
        enter_cameras_id.push(data["id"])
        Data = new Date();
        enter_cameras_time.push([Data.getMinutes(), Data.getSeconds()])
        let video_item = document.createElement("div")
        let img_camera = document.createElement("img")
        video_item.classList.add("video-item")
        // video_item.id = data["id"]
        img_camera.src = "data:image/jpeg;base64, " + data["image"]
        img_camera.id = data["id"]
        video_item.appendChild(img_camera)
        enter_div.appendChild(video_item)
        console.log("ADDED")
    } else {
        Data = new Date();
        // console.log(enter_cameras_time[enter_cameras_id.indexOf(data["id"])])
        enter_cameras_time[enter_cameras_id.indexOf(data["id"])] = [Data.getMinutes(), Data.getSeconds()]
        let img_camera = document.getElementById(data["id"])
        img_camera.src = "data:image/jpeg;base64, " + data["image"]
        console.log("IN")
    }
    console.log(enter_cameras_id)
    // console.log(enter_cameras_time)
}

function check_time() {
    Data = new Date();
    enter_cameras_id.forEach(item => {
        let last_time = enter_cameras_time[enter_cameras_id.indexOf(item)]
        if (Data.getMinutes() - last_time[0] > 0 || Data.getSeconds() - last_time[1] > 1) {
            let img_camera = document.getElementById(item)
            img_camera.src = "/media/not_found.png"
        }
})
}
setInterval(check_time, 10)
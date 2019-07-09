document.write("<script src='/javascripts/jsencrypt.min.js'></script>");

var privateKey = "-----BEGIN RSA PRIVATE KEY-----\nMIICWwIBAAKBgQC5M5llDEzIyEWi4eUdxQqnY6DaPE63TQo/NbUZ+JaMBZLGJyjy\nu7uQbv3tk3o8OmuVbBSDLlBgJVuuFRnucdH4P+oyn9SU8F05M2jNNEc4CZiLepBp\nrgHV7MJLh5xU/2TjuPQOdQEHDIrUajZsXLWtxwh6hiqV1nzsW9IV1FwjCQIDAQAB\nAoGAHCm6k+Ew8/9wh3puiv5hxl6iIU22cq1md4JFTfO9gQF/9l4SHgdqWGZoeu5I\nUkxX+9r5q5Epa9WCgZB35wir8yAbNnez8uOWhAt9sAi1u4lUsoLlmjbX+3WtZM/Y\nO74DF0qzE5vT4/wXm7Njp2NXB/F7X2nPzxaPqYMIAMxE6ZkCQQDbj59hJp237SdK\n6G6R0iPlxpAlGY0MijrRzcAlz/U5OzYYTHrhLLU7IcF5Oxt+ZpCIFEhFWkfCy5VB\nWtHRyASvAkEA1/Ap2hPGbSnZpxu9J16fIenS3Gwy4JoE5P1rclBq6oPBg9LtxKXu\n3u60cAw/46QoYYvvIJ8q7VkToXCKO3UxxwJAPUZd4o0WYyhKWPt5MDUHU68Qt2nk\nFWXWeIsFXwgkle5ScIGXoZQKmBAZoK3ARIx3NaMDcGd7s3+BjhW8jOFXfQJADCKY\nB4Ri+1GFxMlfSO4dXUeJrQ97kHm3WrMPLb5tM76xylm5OPrmQKsDguR9VqqsBkdZ\n6ehn/iyqWME9U3gTkwJAdR0TRN1UtYp/LrT4TG2RPbeyS3HKBVLN4flyVUvNsTbQ\nLD2ErBiLhcG9EaXT2rwiU5j2xcFckhNLaVuif0Je9Q==\n-----END RSA PRIVATE KEY-----"
var publicKey = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC5M5llDEzIyEWi4eUdxQqnY6Da\nPE63TQo/NbUZ+JaMBZLGJyjyu7uQbv3tk3o8OmuVbBSDLlBgJVuuFRnucdH4P+oy\nn9SU8F05M2jNNEc4CZiLepBprgHV7MJLh5xU/2TjuPQOdQEHDIrUajZsXLWtxwh6\nhiqV1nzsW9IV1FwjCQIDAQAB\n-----END PUBLIC KEY-----"
var adminAddress = "adminaddrestadsf"
var voterAddress = ["111111111", "2222222222", "333333333", "444444444", "55555555555"]

function request(method, url, params) {
    let xhr = new XMLHttpRequest();

    xhr.open(method, url, false);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({
        params: params
    }))

    return xhr.responseText;
}

function showVoteInit() {
    let options = [];
    try {
        let tmp = JSON.parse(request('GET', '/api/vote'))
        options = tmp.options;
        document.getElementById("show-deadline").innerHTML = tmp.deadline
    } catch (e) {
        //Do Nothing
    }
    for (let i = 0; i < options.length; i++) {
        document.getElementById("show-option" + i).innerHTML = options[i]
    }

    try {
        let tickets = JSON.parse(request('GET', "/api/ticket")).tickets
        if (tickets.length > 0) {
            let tmpHTML = "";
            for (let i = 0; i < tickets.length; i++) {
                tmpHTML = tmpHTML + "<div>표" + i + ": " + tickets[i] + "</div>"
            }
            document.getElementById("result-ticket").innerHTML = tmpHTML
        }

    } catch (e) {
        // Do Nothing
    }
}

window.onload = function () {
    let addresses = JSON.parse(request('GET', "/api/address"))

    adminAddress = addresses.admin
    voterAddress = addresses.voter

    document.getElementById("admin-address").innerHTML = adminAddress;
    document.getElementById("admin-publicKey").innerHTML = publicKey;
    document.getElementById("admin-privateKey").innerHTML = privateKey;
    for (let i = 0; i < 5; i++) {
        document.getElementById("voter" + i + "-address").innerHTML = voterAddress[i];
    }
    showVoteInit()

}

function createVote() {
    let options = []
    let deadline = document.getElementById("vote-deadline").value;
    let params = {}

    if (deadline.length < 1) {
        alert("투표 기간을 확인하십시오.")
        return;
    }

    for (let i = 0; i < 3; i++) {
        let tmp = document.getElementById("vote-option" + i).value
        if (tmp.length < 1) {
            alert("투표 옵션을 확인하십시오.")
            return;
        } else {
            options.push(tmp);
        }
    }

    params.deadline = deadline;
    params.options = options;

    alert(request("POST", "/api/vote", params))
    showVoteInit()
}

function generatorBallot(target, index) {
    let choice = [0, 0, 0];
    let sum = 0;

    if (target.selectedIndex == 0) {
        document.getElementById("voter" + index + "-ballot").innerHTML = ""
        document.getElementById("voter" + index + "-ballot-encrypt").innerHTML = ""
        return;
    }

    for (let i = 0; i < 3; i++) {
        let tmp = Math.floor(Math.random() * 1000);
        choice[i] = tmp;
        sum = sum + tmp;
    }

    choice[target.selectedIndex - 1] = sum;

    // 객체 생성

    var crypt = new JSEncrypt();
    crypt.setPrivateKey(publicKey);
    crypt.setPublicKey(privateKey);
    var text = crypt.encrypt(choice.toString())

    document.getElementById("voter" + index + "-ballot").innerHTML = choice.toString()
    document.getElementById("voter" + index + "-ballot-encrypt").innerHTML = text
}

function vote(index) {
    let ticket = document.getElementById("voter" + index + "-ballot-encrypt").innerHTML;
    let params = {}

    if (ticket) {
        params.ticket = ticket;
        params.index = index
        alert(request("POST", "/api/ticket", params))
    } else {
        alert("표 내용을 확인하십시오.")
    }
}

function openVote() {
    let params = {
        state: "PROCEEDING"
    }
    alert(request("PUT", "/api/vote", params))
}

function closeVote() {
    let params = {
        state: "CLOSED"
    }
    alert(request("PUT", "/api/vote", params))
    showVoteInit()
}

function countTicket() {
    try {
        let tickets = JSON.parse(request('GET', "/api/ticket")).tickets
        let tmp = ""
        // 객체 생성

        var crypt = new JSEncrypt();
        crypt.setPrivateKey(publicKey);
        crypt.setPublicKey(privateKey);

        for (let i = 0; i < tickets.length; i++) {
            tmp = tmp + crypt.decrypt(tickets[i]) + "<br>"
        }
        document.getElementById("result-decrypt").innerHTML = tmp

    } catch (e) {
        alert("투표가 완료되지 않았습니다.")

    }
}

function showState() {
    alert(request('GET', "/api/state"))
}
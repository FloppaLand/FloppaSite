
        const metadatas = JSON.parse('{{ metadatas | tojson | safe}}');
        const SERVER_IMAGES_BASE = "{{ url_for('static', filename='server_images/') }}"
        const HEADS_BASE = "{{ url_for('head', username='') }}"
        
        const MC_PING_BASE = "https://api.mcstatus.io/v2/status/java/"
        const MODRINTH_BASE = "https://api.modrinth.com/v2/"

        metadatas.forEach( (meta) => {

          $.getJSON(MC_PING_BASE + meta["ping_ip"], info => {
            console.log(info.players)
            player_imgs = info.players.list.map( (player) => {
              return $("<div>", {class: "server_player_head", src: HEADS_BASE + player.name_clean}).append(
                $("<img>", {src: HEADS_BASE + player.name_clean}),
                $("<span>", {class: "server_player_name"}).append(player.name_clean)
              )
            })
            console.log('data: ')
            console.log(info)
            $("#ServerPlates").append($("<div>", {class: "main3_server"}).append(
              $("<img>", {class: "main3_server_img", src: SERVER_IMAGES_BASE + meta.title_image}),
              $("<div>", {class: "main3_server_info"}).append(
                $("<a>", {class: "main3_server_headline"}).append( meta.name ),
                $("<a>", {class: "main3_server_text"}).append( meta.description ),
                $("<hr>", { style: "border: 0; border-top: 3px dotted #bbb; width: 100%"}),
                $("<div>", {class: "main3_server_players_div"}).append(
                  $("<a>", {class: "main3_server_players_count"}).append(info.players.online > 0 ? `Игроки: ${info.players.online}/${info.players.max}` : "Нет игроков" ),
                  player_imgs
                )
              )
            ))
          })
        })
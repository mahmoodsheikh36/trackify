const IS_SMALL_SCREEN = document.documentElement.clientWidth <= 600

async function fetchArtistData(artistName, cb) {
    let response = await fetch(
        '/spotify/artist_discogs_data?' + new URLSearchParams({
            'artist_name': artistName
        })
    )
    let data = await response.json()
    cb(data)
}

async function fetchTopArtists(cb) {
    let response = await fetch(
        `/spotify/top_artists?num_of_artists_to_return=${IS_SMALL_SCREEN ? 10 : 15}`
    )
    let data = await response.json()
    cb(data)
}

async function setupTopArtists() {
    let first = true
    imagesPlaced = []
    fetchTopArtists(topArtists => {
        topArtists.forEach(artist => {
            fetchArtistData(artist.name, data => {
                let containerWidth = $('#top_artists').clientWidth
                let containerHeight = $('#top_artists').clientHeight

                let img = {
                    width: first ? 135 : 85,
                    height: first ? 135 : 85,
                    x: first ? 0.5 * containerWidth - 135 / 2 : undefined,
                    y: first ? 0.5 * containerHeight - 135 / 2 : undefined
                }

                let pass = first
                while (!pass) {
                    let xNew = Math.ceil(Math.random() * containerWidth)
                    let yNew = Math.ceil(Math.random() * containerHeight)
                    img.x = xNew
                    img.y = yNew
                    let overlaps
                    let overflows
                    for (let otherImage of imagesPlaced) {
                        overlaps = (((img.x >= otherImage.x && img.x <= otherImage.x + otherImage.width) ||
                                       (img.x + img.width >= otherImage.x && img.x + img.width <= otherImage.x + otherImage.width)) &&
                                      ((img.y >= otherImage.y && img.y <= otherImage.y + otherImage.height) ||
                                       (img.y + img.height >= otherImage.y && img.y + img.height <= otherImage.y + otherImage.height)))
                        overflows = img.x + img.width > containerWidth || img.y + img.height > containerHeight || img.y - img.height/2 < 0
                        if (overlaps || overflows) {
                            break
                        }
                    }
                    if (!overlaps && !overflows) {
                        pass = true
                    }
                }

                let imgElement = document.createElement('img')
                imgElement.style.position = "absolute"
                imgElement.src = data.thumb || '/static/music_placeholder.png'
                if (first) {
                    imgElement.classList.add('top_artist', 'biggest')
                    first = false
                } else {
                    imgElement.className = 'top_artist'
                }

                imgElement.style.width = img.width+'px'
                imgElement.style.height = img.height+'px'
                imgElement.style.left = img.x + 'px'
                imgElement.style.top = img.y + 'px'

                imagesPlaced.push(img)
                $('#top_artists').appendChild(imgElement)
            })
        })
    })
}

async function setupTopTracks() {
    fetchTopTracks(topTracks => {
        topTracks.forEach(track => {
            let topTrackElement = document.createElement('div')
            topTrackElement.className = 'top_track'
            topTrackElement.innerHTML = `
            <img src="${track.image_url}"/>
            <div class="top_track_desc">
                <a>${track.name}</a>
                <a>${track.artist_name}</a>
            </div>
            `
            $('#top_tracks').appendChild(topTrackElement)
        })
    })
}

async function fetchTopTracks(cb) {
    let response = await fetch(
        '/spotify/top_tracks?num_of_tracks_to_return=5'
    )
    let data = await response.json()
    cb(data)
}

async function setupTotalPlays() {
    setInterval(() => {
        fetchTotalPlays(data => {
            let totalPlays = data['total']
            $('#play_counter').innerHTML = totalPlays.toLocaleString()
        })
    }, 2500)
}

async function fetchTotalPlays(cb) {
    let response = await fetch(
        '/spotify/total_plays'
    )
    let data = await response.json()
    cb(data)
}

window.onload = () => {
    setupTopArtists()
    setupTopTracks()
    setupTotalPlays()
}

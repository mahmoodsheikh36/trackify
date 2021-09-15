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
    imagesPlaced = []
    fetchTopArtists(topArtists => {
        topArtists.forEach((artist, idx) => {
            let containerWidth = $('#top_artists').clientWidth
            let containerHeight = $('#top_artists').clientHeight
            let first = idx === 0
            let img = {
                width: first ? 135 : 85,
                height: first ? 135 : 85,
                x: first ? 0.5 * containerWidth - 135 / 2 : undefined,
                y: first ? 0.5 * containerHeight - 135 / 2 : undefined
            }
            if (first) {
                imagesPlaced.push(img) // we push it here to ensure no other image takes its place
            }

            fetchArtistData(artist.name, data => {
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

                if (!first) {
                    imagesPlaced.push(img)
                }

                let container = document.createElement('div')
                let imgElement = document.createElement('img')
                let titleElement = document.createElement('a')

                imgElement.src = data.thumb || '/static/music_placeholder.png'
                container.style.width = img.width+'px'
                container.style.height = img.height+'px'
                container.style.left = img.x + 'px'
                container.style.top = img.y + 'px'

                if (first) {
                    container.classList.add('top_artist', 'biggest')
                    container.appendChild(imgElement)
                } else {
                    container.className = 'top_artist'

                    let rankElement = document.createElement('div')
                    rankElement.innerHTML = idx + 1
                    rankElement.className = 'artist_rank'
                    rankElement.style.left = img.width - 25 + 'px'

                    container.appendChild(imgElement)
                    container.appendChild(rankElement)
                }

                titleElement.innerHTML = artist.name
                titleElement.className = 'artist_title highlighted_background hidden'
                container.appendChild(titleElement)

                container.onmouseover = () => {
                    titleElement.classList.remove('hidden')
                }
                container.onmouseout = () => {
                    titleElement.classList.add('hidden')
                }
                container.onclick = () => {
                    console.log(data)
                    window.open(`https://www.discogs.com${data.uri}`)
                }

                $('#top_artists').appendChild(container)

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

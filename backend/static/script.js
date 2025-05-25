document.addEventListener('DOMContentLoaded', async () => {
    const birdGridContainer = document.getElementById('bird-grid-container');
    const searchInput = document.getElementById('bird-search-input');
    let allBirds = [];
    let initialQuery = '';

    function getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    async function loadBirdsFromJSON() {
        try {
            const response = await fetch(birdsDataJsonUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("Could not load birds data:", error);
            if (birdGridContainer) {
                birdGridContainer.innerHTML = '<p>Lỗi: Không thể tải dữ liệu các loài chim. Vui lòng thử lại sau.</p>';
            }
            return [];
        }
    }

    function getBirdCategory(bird) {
        // Prioritize bird.title for category if it seems more specific
        const commonNameParts = bird.name.split(' ');
        const titleParts = bird.title ? bird.title.split(' ') : [];
        
        let potentialCategoryWord = "";

        if (titleParts.length > 0) {
            potentialCategoryWord = titleParts[titleParts.length - 1];
        }
        if (!potentialCategoryWord || potentialCategoryWord.toLowerCase() === commonNameParts[commonNameParts.length -1].toLowerCase() || titleParts.length <=1 ) {
             potentialCategoryWord = commonNameParts[commonNameParts.length - 1];
        }


        const commonCategories = ["Albatross", "Ani", "Auklet", "Blackbird", "Bobolink", "Bunting", "Cardinal", "Catbird", "Chat", "Towhee", "Cormorant", "Cowbird", "Creeper", "Crow", "Cuckoo", "Finch", "Flicker", "Flycatcher", "Frigatebird", "Fulmar", "Gadwall", "Goldfinch", "Grackle", "Grebe", "Grosbeak", "Guillemot", "Gull", "Hummingbird", "Jaeger", "Jay", "Junco", "Kingbird", "Kingfisher", "Kittiwake", "Lark", "Loon", "Mallard", "Meadowlark", "Merganser", "Mockingbird", "Nighthawk", "Nutcracker", "Nuthatch", "Oriole", "Ovenbird", "Pelican", "Pewee", "Phoebe", "Pipit", "Puffin", "Raven", "Redstart", "Roadrunner", "Shrike", "Sparrow", "Starling", "Swallow", "Tanager", "Tern", "Thrasher", "Vireo", "Warbler", "Waterthrush", "Waxwing", "Woodpecker", "Wren", "Yellowthroat", "Titmouse", "Heron", "Solitaire", "Duck", "Hawk", "Owl", "Scoter", "Eagle", "Dove", "Chickadee", "Siskin", "Skimmer", "Quail", "Egret", "Teal", "Pigeon", "Turkey", "Crossbill", "Oystercatcher", "Anhinga", "Grouse", "Vulture", "Kite", "Sanderling", "Phalarope", "Crane", "Falcon", "Goose", "Thrush", "Dipper", "Avocet", "Plover", "Gallinule", "Ibis", "Stork", "Godwit", "Swift", "Parakeet", "Sayornis", "Petrochelidon", "Geococcyx", "Aegithalidae"];


        if (bird.name === "Merlin" && bird.description.toLowerCase().includes("mythical figure")) return "MYTHICAL";
        if (bird.name === "Merlin") return "FALCONS";
        if (bird.name === "Redhead" && bird.description.toLowerCase().includes("human hair color")) return "HUMAN TRAIT";
        if (bird.name === "Redhead") return "DUCKS";
        if (bird.name === "Sayornis") return "PHOEBES"; // From title: Sayornis
        if (bird.name === "Petrochelidon") return "SWALLOWS"; // From title: Petrochelidon
        if (bird.name === "Geococcyx") return "ROADRUNNERS"; // From title: Roadrunner
        if (bird.name === "Aegithalidae") return "BUSHTITS"; // From title: Aegithalidae (Bushtits family)


        let categoryText = potentialCategoryWord.toUpperCase();

        if (commonCategories.some(c => c.toLowerCase() === potentialCategoryWord.toLowerCase())) {
            if (potentialCategoryWord.endsWith('s')) { // e.g. Crossbills
                 categoryText = potentialCategoryWord.toUpperCase();
            } else if (potentialCategoryWord.endsWith('y') && potentialCategoryWord.length > 1) { // e.g. Fly -> FLIES
                 categoryText = potentialCategoryWord.slice(0, -1).toUpperCase() + "IES";
            } else if (potentialCategoryWord.toLowerCase() === "goose") {
                 categoryText = "GEESE";
            } else if (potentialCategoryWord.toLowerCase() === "mouse") { // Titmouse
                 categoryText = "TITMICE"
            }
             else {
                 categoryText = potentialCategoryWord.toUpperCase() + "S";
            }
            return categoryText;
        }
        
        if (bird.description.toLowerCase().includes("seabird")) return "SEABIRDS";
        if (bird.description.toLowerCase().includes("songbird")) return "SONGBIRDS";
        if (bird.description.toLowerCase().includes("wading bird")) return "WADERS";
        if (bird.description.toLowerCase().includes("bird of prey") || bird.description.toLowerCase().includes("raptor")) return "RAPTORS";

        return "BIRDS";
    }


    function displayBirds(birdsToDisplay) {
        if (!birdGridContainer) return;
        birdGridContainer.innerHTML = '';

        if (birdsToDisplay.length === 0) {
            birdGridContainer.innerHTML = '<p>Không tìm thấy loài chim nào phù hợp.</p>';
            return;
        }

        birdsToDisplay.forEach(bird => {
            const card = document.createElement('div');
            card.className = 'bird-card';
            card.setAttribute('role', 'link');
            card.setAttribute('tabindex', '0'); // Make it focusable
            card.setAttribute('aria-label', `Xem chi tiết về ${bird.name}`);


            card.addEventListener('click', () => {
                const detailUrl = birdDetailBaseUrl.replace('PLACEHOLDER', encodeURIComponent(bird.name));
                window.location.href = detailUrl;
            });
            card.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                            event.preventDefault();
                            const detailUrl = birdDetailBaseUrl.replace('PLACEHOLDER', encodeURIComponent(bird.name));
                            window.location.href = detailUrl;
                        }
        });

            const img = document.createElement('img');
            img.className = 'card-bg-image';
            img.src = bird.image_url || 'https://via.placeholder.com/260x360?text=No+Image'; // Placeholder with similar aspect ratio
            img.alt = bird.name; 

            const overlay = document.createElement('div');
            overlay.className = 'bird-card-overlay';

            const nameH3 = document.createElement('h3');
            nameH3.textContent = bird.name;

            const categoryP = document.createElement('p');
            categoryP.className = 'bird-category';
            categoryP.textContent = getBirdCategory(bird);

            overlay.appendChild(nameH3);
            overlay.appendChild(categoryP);

            card.appendChild(img);
            card.appendChild(overlay);
            birdGridContainer.appendChild(card);
        });
    }
    
    function handleSearchInput() {
        if (!searchInput) return;
        const keyword = searchInput.value.trim().toLowerCase();
        
        const url = new URL(window.location);
        if (keyword) {
            url.searchParams.set('query', keyword);
        } else {
            url.searchParams.delete('query');
        }
        window.history.replaceState({}, '', url);

        const filteredBirds = allBirds.filter(bird =>
            bird.name.toLowerCase().includes(keyword) ||
            (bird.title && bird.title.toLowerCase().includes(keyword)) ||
            (bird.description && bird.description.toLowerCase().includes(keyword)) // Search in description too
        );
        displayBirds(filteredBirds);
    }

    async function init() {
        allBirds = await loadBirdsFromJSON();
        
        initialQuery = getQueryParam('query');
        if (searchInput && initialQuery) {
            searchInput.value = initialQuery;
             const filteredBirds = allBirds.filter(bird =>
                bird.name.toLowerCase().includes(initialQuery.toLowerCase()) ||
                (bird.title && bird.title.toLowerCase().includes(initialQuery.toLowerCase())) ||
                (bird.description && bird.description.toLowerCase().includes(initialQuery.toLowerCase()))
            );
            displayBirds(filteredBirds);
        } else {
            displayBirds(allBirds);
        }

        if (searchInput) {
            searchInput.addEventListener('input', handleSearchInput);
        }
    }

    init();
});
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
            // Đảm bảo biến birdsDataJsonUrl đã được định nghĩa
            if (typeof birdsDataJsonUrl === 'undefined') {
                console.error("birdsDataJsonUrl is not defined. Please define it.");
                if (birdGridContainer) {
                     birdGridContainer.innerHTML = '<p>Lỗi cấu hình: Đường dẫn dữ liệu chưa được thiết lập.</p>';
                }
                return [];
            }
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
        const commonNameParts = bird.name.split(' ');
        const titleParts = bird.title ? bird.title.split(' ') : [];
        
        let potentialCategoryWord = "";

        if (titleParts.length > 0) {
            potentialCategoryWord = titleParts[titleParts.length - 1];
        }
        // Kiểm tra commonNameParts có phần tử không trước khi truy cập
        if ((!potentialCategoryWord || (commonNameParts.length > 0 && potentialCategoryWord.toLowerCase() === commonNameParts[commonNameParts.length -1].toLowerCase()) || titleParts.length <=1) && commonNameParts.length > 0) {
             potentialCategoryWord = commonNameParts[commonNameParts.length - 1];
        }


        const commonCategories = ["Albatross", "Ani", "Auklet", "Blackbird", "Bobolink", "Bunting", "Cardinal", "Catbird", "Chat", "Towhee", "Cormorant", "Cowbird", "Creeper", "Crow", "Cuckoo", "Finch", "Flicker", "Flycatcher", "Frigatebird", "Fulmar", "Gadwall", "Goldfinch", "Grackle", "Grebe", "Grosbeak", "Guillemot", "Gull", "Hummingbird", "Jaeger", "Jay", "Junco", "Kingbird", "Kingfisher", "Kittiwake", "Lark", "Loon", "Mallard", "Meadowlark", "Merganser", "Mockingbird", "Nighthawk", "Nutcracker", "Nuthatch", "Oriole", "Ovenbird", "Pelican", "Pewee", "Phoebe", "Pipit", "Puffin", "Raven", "Redstart", "Roadrunner", "Shrike", "Sparrow", "Starling", "Swallow", "Tanager", "Tern", "Thrasher", "Vireo", "Warbler", "Waterthrush", "Waxwing", "Woodpecker", "Wren", "Yellowthroat", "Titmouse", "Heron", "Solitaire", "Duck", "Hawk", "Owl", "Scoter", "Eagle", "Dove", "Chickadee", "Siskin", "Skimmer", "Quail", "Egret", "Teal", "Pigeon", "Turkey", "Crossbill", "Oystercatcher", "Anhinga", "Grouse", "Vulture", "Kite", "Sanderling", "Phalarope", "Crane", "Falcon", "Goose", "Thrush", "Dipper", "Avocet", "Plover", "Gallinule", "Ibis", "Stork", "Godwit", "Swift", "Parakeet", "Sayornis", "Petrochelidon", "Geococcyx", "Aegithalidae"];


        if (bird.name === "Merlin" && bird.description && bird.description.toLowerCase().includes("mythical figure")) return "MYTHICAL";
        if (bird.name === "Merlin") return "FALCONS";
        if (bird.name === "Redhead" && bird.description && bird.description.toLowerCase().includes("human hair color")) return "HUMAN TRAIT";
        if (bird.name === "Redhead") return "DUCKS";
        if (bird.name === "Sayornis") return "PHOEBES"; 
        if (bird.name === "Petrochelidon") return "SWALLOWS";
        if (bird.name === "Geococcyx") return "ROADRUNNERS"; 
        if (bird.name === "Aegithalidae") return "BUSHTITS";


        let categoryText = potentialCategoryWord.toUpperCase();

        if (commonCategories.some(c => c.toLowerCase() === potentialCategoryWord.toLowerCase())) {
            if (potentialCategoryWord.endsWith('s')) { 
                 categoryText = potentialCategoryWord.toUpperCase();
            } else if (potentialCategoryWord.endsWith('y') && potentialCategoryWord.length > 1) { 
                 categoryText = potentialCategoryWord.slice(0, -1).toUpperCase() + "IES";
            } else if (potentialCategoryWord.toLowerCase() === "goose") {
                 categoryText = "GEESE";
            } else if (potentialCategoryWord.toLowerCase() === "mouse") { 
                 categoryText = "TITMICE"
            }
             else {
                 categoryText = potentialCategoryWord.toUpperCase() + "S";
            }
            return categoryText;
        }
        
        if (bird.description && bird.description.toLowerCase().includes("seabird")) return "SEABIRDS";
        if (bird.description && bird.description.toLowerCase().includes("songbird")) return "SONGBIRDS";
        if (bird.description && bird.description.toLowerCase().includes("wading bird")) return "WADERS";
        if (bird.description && (bird.description.toLowerCase().includes("bird of prey") || bird.description.toLowerCase().includes("raptor"))) return "RAPTORS";

        return "BIRDS"; // Default category
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
            card.setAttribute('tabindex', '0'); 
            card.setAttribute('aria-label', `Xem chi tiết về ${bird.name}`);

            card.addEventListener('click', () => {
                // Đảm bảo biến birdDetailBaseUrl đã được định nghĩa
                if (typeof birdDetailBaseUrl === 'undefined') {
                    console.error("birdDetailBaseUrl is not defined.");
                    return;
                }
                const detailUrl = birdDetailBaseUrl.replace('PLACEHOLDER', encodeURIComponent(bird.name));
                window.location.href = detailUrl;
            });
            card.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    if (typeof birdDetailBaseUrl === 'undefined') {
                        console.error("birdDetailBaseUrl is not defined.");
                        return;
                    }
                    const detailUrl = birdDetailBaseUrl.replace('PLACEHOLDER', encodeURIComponent(bird.name));
                    window.location.href = detailUrl;
                }
            });

            const img = document.createElement('img');
            img.className = 'card-bg-image';
            img.src = bird.image_url || 'https://via.placeholder.com/260x360?text=No+Image';
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
    
    /**
     * Lọc danh sách chim dựa trên từ khóa.
     * Tìm kiếm trong các trường: name, title, description, identification (mảng),
     * habitat, diet, behavior, conservation_status.
     * @param {Array} birds - Mảng các đối tượng chim để lọc.
     * @param {string} keyword - Từ khóa tìm kiếm.
     * @returns {Array} - Mảng các đối tượng chim phù hợp với từ khóa.
     */
    function filterBirdsByKeyword(birds, keyword) {
        if (!keyword) {
            return birds; // Trả về tất cả nếu không có từ khóa
        }
        const keywordLower = keyword.toLowerCase();

        return birds.filter(bird => {
            // Tìm trong tên (bắt buộc phải có)
            if (bird.name && bird.name.toLowerCase().includes(keywordLower)) return true;
            
            // Tìm trong tiêu đề (nếu có)
            if (bird.title && typeof bird.title === 'string' && bird.title.toLowerCase().includes(keywordLower)) return true;
            
            // Tìm trong mô tả (nếu có)
            if (bird.description && typeof bird.description === 'string' && bird.description.toLowerCase().includes(keywordLower)) return true;
            
            // Tìm trong mảng nhận dạng (nếu có)
            if (bird.identification && Array.isArray(bird.identification)) {
                if (bird.identification.some(id => typeof id === 'string' && id.toLowerCase().includes(keywordLower))) return true;
            }
            
            // Tìm trong môi trường sống (nếu có)
            if (bird.habitat && typeof bird.habitat === 'string' && bird.habitat.toLowerCase().includes(keywordLower)) return true;
            
            // Tìm trong chế độ ăn (nếu có)
            if (bird.diet && typeof bird.diet === 'string' && bird.diet.toLowerCase().includes(keywordLower)) return true;
            
            // Tìm trong hành vi (nếu có)
            if (bird.behavior && typeof bird.behavior === 'string' && bird.behavior.toLowerCase().includes(keywordLower)) return true;
            
            // Tìm trong tình trạng bảo tồn (nếu có)
            if (bird.conservation_status && typeof bird.conservation_status === 'string' && bird.conservation_status.toLowerCase().includes(keywordLower)) return true;
            
            return false; // Không tìm thấy ở bất kỳ trường nào
        });
    }

    function handleSearchInput() {
        if (!searchInput) return;
        const keyword = searchInput.value.trim(); // Giữ keyword gốc cho URL
        
        const url = new URL(window.location);
        if (keyword) {
            url.searchParams.set('query', keyword);
        } else {
            url.searchParams.delete('query');
        }
        window.history.replaceState({}, '', url);


        const filteredBirds = filterBirdsByKeyword(allBirds, keyword);
        displayBirds(filteredBirds);
    }

    async function init() {
        allBirds = await loadBirdsFromJSON();
        
        initialQuery = getQueryParam('query');

        if (searchInput) {
            if (initialQuery) {
                searchInput.value = initialQuery;
            }
            
            // Lọc dựa trên giá trị hiện tại của searchInput (có thể là initialQuery hoặc giá trị được trình duyệt khôi phục)
            const currentSearchTerm = searchInput.value.trim();
            if (currentSearchTerm) {
                const filteredBirds = filterBirdsByKeyword(allBirds, currentSearchTerm);
                displayBirds(filteredBirds);
            } else {
                displayBirds(allBirds); // Hiển thị tất cả nếu không có query và input rỗng
            }

            searchInput.addEventListener('input', handleSearchInput);
        } else {
            // Nếu không có searchInput element, lọc dựa trên initialQuery (nếu có) hoặc hiển thị tất cả
            if (initialQuery) {
                 const filteredBirds = filterBirdsByKeyword(allBirds, initialQuery);
                 displayBirds(filteredBirds);
            } else {
                displayBirds(allBirds);
            }
        }
    }
    init();
});

// Static Location Data for Manual Entry
// Used for cascading dropdowns: Country -> State -> District -> Taluk

const LOCATION_DATA = {
    "India": {
        "Tamil Nadu": {
            "Ariyalur": ["Ariyalur", "Udayarpalayam", "Sendurai"],
            "Chengalpattu": ["Chengalpattu", "Tambaram", "Pallavaram", "Thiruporur", "Madurantakam", "Cheyyur"],
            "Chennai": ["Aminjikarai", "Ayanavaram", "Egmore", "Guindy", "Madhavaram", "Mylapore", "Perambur", "Purasawalkam", "Tondiarpet", "Velachery"],
            "Coimbatore": ["Coimbatore North", "Coimbatore South", "Mettupalayam", "Pollachi", "Sulur", "Valparai"],
            "Cuddalore": ["Cuddalore", "Chidambaram", "Kattumannarkoil", "Kurinjipadi", "Panruti", "Titakudi", "Veppur"],
            "Dharmapuri": ["Dharmapuri", "Harur", "Karimangalam", "Nallampalli", "Palacode", "Pennagaram"],
            "Dindigul": ["Dindigul", "Kodaikanal", "Natham", "Nilakkottai", "Oddanchatram", "Palani", "Vedasandur"],
            "Erode": ["Erode", "Anthiyur", "Bhavani", "Gobichettipalayam", "Kodumudi", "Modakkurichi", "Perundurai", "Sathyamangalam", "Thalavadi"],
            "Kallakurichi": ["Kallakurichi", "Chinnasalem", "Sankarapuram", "Tirukkoyilur", "Ulundurpet"],
            "Kanchipuram": ["Kanchipuram", "Kundrathur", "Sriperumbudur", "Uthiramerur", "Walajabad"],
            "Kanyakumari": ["Agastheeswaram", "Kalkulam", "Killiyur", "Thiruvattar", "Thovalai", "Vilavancode"],
            "Karur": ["Karur", "Aravakurichi", "Kadavur", "Krishnarayapuram", "Kulithalai", "Manmangalam", "Pugalur"],
            "Krishnagiri": ["Krishnagiri", "Bargur", "Hosur", "Pochampalli", "Sulagiri", "Thenkanikottai", "Uthangarai"],
            "Madurai": ["Madurai North", "Madurai South", "Madurai East", "Madurai West", "Melur", "Peraiyur", "Thirumangalam", "Thiruparankundram", "Usilampatti", "Vadipatti"],
            "Nagapattinam": ["Nagapattinam", "Kilvelur", "Thirukuvalai", "Vedaranyam"],
            "Namakkal": ["Namakkal", "Kollimalai", "Kumarapalayam", "Mohanur", "Paramathi Velur", "Rasipuram", "Senthamangalam", "Tiruchengode"],
            "Perambalur": ["Perambalur", "Alathur", "Kunnam", "Veppanthattai"],
            "Pudukkottai": ["Pudukkottai", "Alangudi", "Aranthangi", "Avudaiyarkoil", "Gandarvakottai", "Iluppur", "Karambakkudi", "Kulathur", "Manamelkudi", "Ponnamaravathi", "Thirumayam"],
            "Ramanathapuram": ["Ramanathapuram", "Kadaladi", "Kamuthi", "Keezhakarai", "Mudukulathur", "Paramakudi", "Rajasingamangalam", "Rameswaram", "Tiruvadanai"],
            "Ranipet": ["Ranipet", "Arakkonam", "Arcot", "Nemili", "Sholinghur", "Walajah"],
            "Salem": ["Salem", "Salem South", "Salem West", "Attur", "Edappadi", "Gangavalli", "Kadaiyampatti", "Mettur", "Omalur", "Pethanaickenpalayam", "Sankari", "Vazhapadi", "Yercaud"],
            "Sivaganga": ["Sivaganga", "Devakottai", "Ilayangudi", "Kalaiyarkoil", "Karaikudi", "Manamadurai", "Singampunari", "Tirupathur", "Thirupuvanam"],
            "Tenkasi": ["Tenkasi", "Alangulam", "Kadayanallur", "Sankarankovil", "Shenkottai", "Sivagiri", "Thiruvengadam", "Veerakeralampudur"],
            "Thanjavur": ["Thanjavur", "Boothalur", "Kumbakonam", "Orathanadu", "Papanasam", "Pattukkottai", "Peravurani", "Thiruvaiyaru", "Thiruvidaimarudur"],
            "The Nilgiris": ["Udhagamandalam", "Coonoor", "Gudalur", "Kotagiri", "Kundah", "Pandalur"],
            "Theni": ["Theni", "Andipatti", "Bodinayakanur", "Periyakulam", "Uthamapalayam"],
            "Thiruvallur": ["Thiruvallur", "Avadi", "Gummidipoondi", "Pallipattu", "Ponneri", "Poonamallee", "R.K. Pet", "Tiruttani", "Uthukkottai"],
            "Thiruvarur": ["Thiruvarur", "Kodavasal", "Koothanallur", "Mannargudi", "Nannilam", "Needamangalam", "Thiruthuraipoondi", "Valangaiman"],
            "Thoothukudi": ["Thoothukudi", "Eral", "Ettayapuram", "Kayathar", "Kovilpatti", "Ottapidaram", "Sathankulam", "Srivaikundam", "Tiruchendur", "Vilathikulam"],
            "Tiruchirappalli": ["Tiruchirappalli", "Lalgudi", "Manachanallur", "Manapparai", "Marungapuri", "Musiri", "Srirangam", "Thiruverumbur", "Thuraiyur"],
            "Tirunelveli": ["Tirunelveli", "Ambasamudram", "Cheranmahadevi", "Manur", "Nanguneri", "Palayamkottai", "Radhapuram", "Thisayanvilai"],
            "Tirupathur": ["Tirupathur", "Ambur", "Natrampalli", "Vaniyambadi"],
            "Tiruppur": ["Tiruppur North", "Tiruppur South", "Avinashi", "Dharapuram", "Kangeyam", "Madathukulam", "Palladam", "Udumalaipettai", "Uthukuli"],
            "Tiruvannamalai": ["Tiruvannamalai", "Arani", "Chengam", "Chetpet", "Cheyyar", "Jamunamarathur", "Kalasapakkam", "Kilpennathur", "Polur", "Thandarampattu", "Vandavasi", "Vembakkam"],
            "Vellore": ["Vellore", "Anaicut", "Gudiyatham", "K.V. Kuppam", "Katpadi", "Pernambut"],
            "Viluppuram": ["Viluppuram", "Gingee", "Kandachipuram", "Marakkanam", "Melmalaiyanur", "Thiruvennainallur", "Tindivanam", "Vanur", "Vikravandi"],
            "Virudhunagar": ["Virudhunagar", "Aruppukkottai", "Kariapatti", "Rajapalayam", "Sathur", "Sivakasi", "Srivilliputhur", "Tiruchuli", "Vembakottai", "Watrap"]
        }
    }
};

// Auto-fill form selects
function initLocationDropdowns(countryId, stateId, districtId, talukId) {
    const countrySel = document.getElementById(countryId);
    const stateSel = document.getElementById(stateId);
    const districtSel = document.getElementById(districtId);
    const talukSel = document.getElementById(talukId);
    
    // Clear all
    countrySel.innerHTML = '<option value="">Select Country</option>';
    
    // Populate Countries
    for (let country in LOCATION_DATA) {
        countrySel.innerHTML += `<option value="${country}">${country}</option>`;
    }
    
    countrySel.addEventListener("change", () => {
        stateSel.innerHTML = '<option value="">Select State</option>';
        districtSel.innerHTML = '<option value="">Select District</option>';
        talukSel.innerHTML = '<option value="">Select Taluk</option>';
        
        if (countrySel.value && LOCATION_DATA[countrySel.value]) {
            for (let state in LOCATION_DATA[countrySel.value]) {
                stateSel.innerHTML += `<option value="${state}">${state}</option>`;
            }
        }
    });
    
    stateSel.addEventListener("change", () => {
        districtSel.innerHTML = '<option value="">Select District</option>';
        talukSel.innerHTML = '<option value="">Select Taluk</option>';
        
        if (stateSel.value && LOCATION_DATA[countrySel.value][stateSel.value]) {
            for (let district in LOCATION_DATA[countrySel.value][stateSel.value]) {
                districtSel.innerHTML += `<option value="${district}">${district}</option>`;
            }
        }
    });
    
    districtSel.addEventListener("change", () => {
        talukSel.innerHTML = '<option value="">Select Taluk</option>';
        
        if (districtSel.value && LOCATION_DATA[countrySel.value][stateSel.value][districtSel.value]) {
            LOCATION_DATA[countrySel.value][stateSel.value][districtSel.value].forEach(taluk => {
                talukSel.innerHTML += `<option value="${taluk}">${taluk}</option>`;
            });
        }
    });
}

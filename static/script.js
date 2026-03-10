function showContent(category) {
    let title, scheduleText, articles;

    // Đặt class 'active' cho liên kết được chọn
    document.querySelectorAll('nav a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-category') === category) {
            link.classList.add('active');
        }
    });

    if (category === 'friendly') {
        title = 'Euro/Copa America';
        scheduleText = `
            <h3>Lịch Thi Đấu 2025</h3>
            <p class="timestamp">Cập nhật: 06:44 AM, 10/05/2025</p>
            <div class="match-list">
                <div class="match-item">
                    <span class="date">10/05/2025</span>
                    <span class="team">Brazil </span>
                    <span class="vs">vs</span>
                    <span class="team"> Argentina</span>
                </div>
                <div class="match-item">
                    <span class="date">10/05/2025</span>
                    <span class="team">USA </span>
                    <span class="vs">vs</span>
                    <span class="team"> Mexico </span>
                </div>
                <div class="match-item">
                    <span class="date">12/05/2025</span>
                    <span class="team">France </span>
                    <span class="vs">vs</span>
                    <span class="team"> Italy </span>
                </div>
                <div class="match-item">
                    <span class="date">14/05/2025</span>
                    <span class="team">Germany </span>
                    <span class="vs">vs</span>
                    <span class="team"> Netherlands </span>
                </div>
                <div class="match-item">
                    <span class="date">07/06/2025</span>
                    <span class="team">England </span>
                    <span class="vs">vs</span>
                    <span class="team"> Senegal </span>
                </div>
                <div class="match-item">
                    <span class="date">10/06/2025</span>
                    <span class="team">Spain </span>
                    <span class="vs">vs</span>
                    <span class="team"> France </span>
                </div>
                <div class="match-item">
                    <span class="date">06/06/2025</span>
                    <span class="team">Hungary </span>
                    <span class="vs">vs</span>
                    <span class="team"> Sweden </span>
                </div>
                <div class="match-item">
                    <span class="date">03/09/2025</span>
                    <span class="team">Portugal </span>
                    <span class="vs">vs</span>
                    <span class="team"> Belgium </span>
                </div>
                <div class="match-item">
                    <span class="date">05/09/2025</span>
                    <span class="team">Japan </span>
                    <span class="vs">vs</span>
                    <span class="team"> South Korea </span>
                </div>
                <div class="match-item">
                    <span class="date">07/10/2025</span>
                    <span class="team">Argentina </span>
                    <span class="vs">vs</span>
                    <span class="team"> Colombia </span>
                </div>
                <div class="match-item">
                    <span class="date">10/10/2025</span>
                    <span class="team">Brazil </span>
                    <span class="vs">vs</span>
                    <span class="team"> Chile </span>
                </div>
                <div class="match-item">
                    <span class="date">14/11/2025</span>
                    <span class="team">England </span>
                    <span class="vs">vs</span>
                    <span class="team"> Germany </span>
                </div>
                <div class="match-item">
                    <span class="date">17/11/2025</span>
                    <span class="team">Italy </span>
                    <span class="vs">vs</span>
                    <span class="team"> Spain </span>
                </div>
                <div class="match-item">
                    <span class="date">02/06/2025</span>
                    <span class="team">USA </span>
                    <span class="vs">vs</span>
                    <span class="team"> Canada </span>
                </div>
                <div class="match-item">
                    <span class="date">04/06/2025</span>
                    <span class="team">Mexico </span>
                    <span class="vs">vs</span>
                    <span class="team"> Costa Rica </span>
                </div>
                <div class="match-item">
                    <span class="date">09/09/2025</span>
                    <span class="team">France </span>
                    <span class="vs">vs</span>
                    <span class="team"> Portugal </span>
                </div>
                <div class="match-item">
                    <span class="date">10/09/2025</span>
                    <span class="team">Germany </span>
                    <span class="vs">vs</span>
                    <span class="team"> Poland </span>
                </div>
            </div>
        `;
        articles = `
            <div class="article" onclick="window.location.href=matchUrls['brazil-argentina-2025']">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkgYyNCcZ9Sc7kXeCPe0hnPVYaT4C7YomBNw&s" alt="Brazil vs Argentina">
                <h3 onclick="navigateToArticle('brazil-argentina')">Brazil đối đầu Argentina trận giao hữu đỉnh cao</h3>
                <p>Trận giao hữu giữa Brazil và Argentina diễn ra vào ngày 10/05/2025 tại São Paulo, hứa hẹn kịch tính.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['usa-mexico-2025']">
                <img src="https://thethaovanhoa.mediacdn.vn/Upload/agUdzah0nJmdL3rsYfrpw/files/2021/08/MYvsMEXICO.jpg" alt="USA vs Mexico">
                <h3 onclick="navigateToArticle('usa-mexico')">Cuộc chiến không khoang nhượng trên đất Mỹ</h3>
                <p>Đội tuyển Mỹ đánh bại Mexico với tỷ số 1-0 vào ngày 10/05/2025 tại Los Angeles.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['france-italy-2025']">
                <img src="https://cdn.bongdaplus.vn/Assets/Media/2023/06/20/97/Phap-vs-Italia-nhan-dinh.jpg" alt="France đối đầu Italy trong trận giao hữu đỉnh cao">
                <h3 onclick="navigateToArticle('france-italy')">France đối đầu Italy trong trận giao hữu đỉnh cao</h3>
                <p>Trận giao hữu giữa France và Italy dự kiến vào ngày 12/05/2025 tại Paris.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['germany-netherlands-2025']">
                <img src="https://media.vov.vn/sites/default/files/styles/front_large/public/2021-06/2021-06-02t191200z_923318475_up1eh621hbzno_rtrmadp_3_soccer-friendly-nld-sco-report.jpg?resize=p_8,w_" alt="Germany vs Netherlands">
                <h3 onclick="navigateToArticle('germany-netherlands')">Germany gặp Netherlands trong trận giao hữu</h3>
                <p>Trận giao hữu giữa Germany và Netherlands dự kiến vào ngày 14/05/2025 tại Berlin.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['england-senegal-2025']">
                <img src="https://e0.365dm.com/22/12/1600x900/skysports-england-senegal-world-cup_5986769.jpg?20221204200226" alt="England vs Senegal">
                <h3 onclick="navigateToArticle('england-senegal')">England đối đầu Senegal tại The City Ground</h3>
                <p>Trận giao hữu giữa England và Senegal diễn ra vào ngày 07/06/2025.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['spain-france-2025']">
                <img src="https://cdn.baohatinh.vn/images/3e71e16a1401e4dc5e668db027ed9ebcbf9216538c4d01309ff089019fb1f33a4784ae14fdd7ec6f68261537a5936941ffc9c1532366a164d43283f732b5036b/tbn-vs-phap3-2328.jpg" alt="Spain vs France">
                <h3 onclick="navigateToArticle('spain-france')">Spain đối đầu France tại Stuttgart</h3>
                <p>Trận giao hữu giữa Spain và France dự kiến vào ngày 10/06/2025.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['hungary-sweden-2025']">
                <img src="https://md.p0.jar15.joymo.no/public/VzIFad2Sq29SnFONF1Mj/WSEC-2024-9-2-Match-18-Hungary-vs-Sweden.jpg" alt="Hungary vs Sweden">
                <h3 onclick="navigateToArticle('hungary-sweden')">Hungary có cơ hội trả nợ Sweden</h3>
                <p>Trận giao hữu giữa Hungary và Sweden dự kiến vào ngày 06/06/2025.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['portugal-belgium-2025']">
                <img src="https://d2x51gyc4ptf2q.cloudfront.net/content/uploads/2021/06/27224236/Belgium-celebrate-knocking-Portugal-out-of-Euro-2020.jpg" alt="Portugal vs Belgium">
                <h3 onclick="navigateToArticle('portugal-belgium')">Portugal giải quyết ân oán Belgium</h3>
                <p>Trận giao hữu giữa Portugal và Belgium dự kiến vào ngày 03/09/2025.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['japan-southkorea-2025']">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTW0jfpOmNn3YImR5xWj5CbNoS9A-rJi1-vnA&s" alt="Japan vs South Korea">
                <h3 onclick="navigateToArticle('japan-southkorea')">Japan đối mặt South Korea</h3>
                <p>Trận giao hữu giữa Japan và South Korea dự kiến vào ngày 05/09/2025.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['argentina-colombia-2025']">
                <img src="https://img.cand.com.vn/resize/800x800/NewFiles/Images/2024/07/15/REUTERS-1721016762212.jpg" alt="Argentina vs Colombia">
                <h3 onclick="navigateToArticle('argentina-colombia')">Argentina đối đầu Colombia</h3>
                <p>Trận giao hữu giữa Argentina và Colombia dự kiến vào ngày 07/10/2025.</p>
            </div>
        `;
    } else if (category === 'uefa') {
        title = 'UEFA Champions League';
        scheduleText = `
            <h3>Lịch Thi Đấu 2025</h3>
            <p class="timestamp">Cập nhật: 06:44 AM, 10/05/2025</p>
            <div class="match-list">
                <div class="match-item">
                    <span class="date">31/05/2025</span>
                    <span class="team">PSG </span>
                    <span class="vs">vs</span>
                    <span class="team"> Inter Milan </span>
                </div>
                <div class="match-item">
                    <span class="date">16/09/2025</span>
                    <span class="team">Manchester City </span>
                    <span class="vs">vs</span>
                    <span class="team"> Ajax </span>
                </div>
                <div class="match-item">
                    <span class="date">16/09/2025</span>
                    <span class="team">Arsenal </span>
                    <span class="vs">vs</span>
                    <span class="team"> Benfica </span>
                </div>
                <div class="match-item">
                    <span class="date">17/09/2025</span>
                    <span class="team">Liverpool </span>
                    <span class="vs">vs</span>
                    <span class="team"> Sporting CP </span>
                </div>
                <div class="match-item">
                    <span class="date">17/09/2025</span>
                    <span class="team">Galatasaray </span>
                    <span class="vs">vs</span>
                    <span class="team"> Barcelona </span>
                </div>
                <div class="match-item">
                    <span class="date">30/09/2025</span>
                    <span class="team">Fenerbahçe </span>
                    <span class="vs">vs</span>
                    <span class="team"> PSG </span>
                </div>
                <div class="match-item">
                    <span class="date">30/09/2025</span>
                    <span class="team">Inter Milan </span>
                    <span class="vs">vs</span>
                    <span class="team"> Manchester United </span>
                </div>
                <div class="match-item">
                    <span class="date">01/10/2025</span>
                    <span class="team">Tottenham </span>
                    <span class="vs">vs</span>
                    <span class="team"> Bayern Munich </span>
                </div>
                <div class="match-item">
                    <span class="date">01/10/2025</span>
                    <span class="team">Chelsea </span>
                    <span class="vs">vs</span>
                    <span class="team"> Real Madrid </span>
                </div>
                <div class="match-item">
                    <span class="date">21/10/2025</span>
                    <span class="team">Ajax </span>
                    <span class="vs">vs</span>
                    <span class="team"> Liverpool </span>
                </div>
                <div class="match-item">
                    <span class="date">21/10/2025</span>
                    <span class="team">Benfica </span>
                    <span class="vs">vs</span>
                    <span class="team"> Galatasaray </span>
                </div>
                <div class="match-item">
                    <span class="date">22/10/2025</span>
                    <span class="team">Sporting CP </span>
                    <span class="vs">vs</span>
                    <span class="team"> Fenerbahçe </span>
                </div>
                <div class="match-item">
                    <span class="date">22/10/2025</span>
                    <span class="team">Barcelona </span>
                    <span class="vs">vs</span>
                    <span class="team"> Manchester City </span>
                </div>
                <div class="match-item">
                    <span class="date">04/11/2025</span>
                    <span class="team">PSG </span>
                    <span class="vs">vs</span>
                    <span class="team"> Arsenal </span>
                </div>
                <div class="match-item">
                    <span class="date">04/11/2025</span>
                    <span class="team">Inter Milan </span>
                    <span class="vs">vs</span>
                    <span class="team"> Tottenham </span>
                </div>
                <div class="match-item">
                    <span class="date">05/11/2025</span>
                    <span class="team">Manchester United </span>
                    <span class="vs">vs</span>
                    <span class="team"> Chelsea </span>
                </div>
                <div class="match-item">
                    <span class="date">05/11/2025</span>
                    <span class="team">Bayern Munich </span>
                    <span class="vs">vs</span>
                    <span class="team"> Real Madrid </span>
                </div>
            </div>
        `;
        articles = `
            <div class="article" onclick="window.location.href=matchUrls['psg-inter-2025']">
                <img src="https://cdn.bongdaplus.vn/Assets/Media/2025/05/10/42/psg-inter.jpg" alt="PSG vs Inter Milan">
                <h3 onclick="navigateToArticle('psg-inter')">PSG liệu có thể đánh bại Inter Milan tại CK UEFA Champions League</h3>
                <p>Theo dự đoán PSG giành chiến thắng 3-1 trước Inter Milan vào ngày 31/05/2025 tại Allianz Arena, Munich, trở thành đội Pháp thứ hai vô địch giải đấu.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['manchester-city-ajax-2025']">
                <img src="https://footballia.eu/cache/matches/1d031569ad628b73a178bdb7b0cf85f2.png" alt="Man City vs Ajax">
                <h3 onclick="navigateToArticle('manchester-city-ajax')">Manchester City đối đầu Ajax tại vòng bảng</h3>
                <p>Trận đấu vòng bảng giữa Manchester City và Ajax dự kiến vào ngày 16/09/2025 tại Etihad Stadium.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['arsenal-benfica-2025']">
                <img src="https://media.vietnamplus.vn/images/ac883ebb7889b1a4222bb1c88021ac11d48198f296d4363f7320973a78212730f273d933fcc8c6d92d3fda5ffae708eacdb57feb901aea868e56e8a402356a73/PSGvsARsenal.jpg" alt="Arsenal vs Benfica">
                <h3 onclick="navigateToArticle('arsenal-benfica')">Arsenal chạm trán Benfica ở vòng bảng</h3>
                <p>Arsenal sẽ đối đầu với Benfica vào ngày 16/09/2025 tại Emirates Stadium trong khuôn khổ vòng bảng.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['liverpool-sporting-2025']">
                <img src="https://a.espncdn.com/combiner/i?img=/photo/2019/0725/r574608_1296x729_16-9.jpg&cquality=80&h=370&w=655" alt="Liverpool vs Sporting CP">
                <h3 onclick="navigateToArticle('liverpool-sporting')">Liverpool gặp Sporting CP tại Anfield</h3>
                <p>Trận đấu giữa Liverpool và Sporting CP dự kiến vào ngày 17/09/2025 tại Anfield.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['galatasaray-barcelona-2025']">
                <img src="https://i.eurosport.com/2022/03/10/3335321-68186688-2560-1440.jpg" alt="Galatasaray vs Barcelona">
                <h3 onclick="navigateToArticle('galatasaray-barcelona')">Galatasaray đối đầu Barcelona tại Istanbul</h3>
                <p>Galatasaray sẽ tiếp Barcelona vào ngày 17/09/2025 trong khuôn khổ vòng bảng UEFA Champions League.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['fenerbahce-psg-2025']">
                <img src="https://i.ytimg.com/vi/rqu_bsQwvTw/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLCLy7LZZmdA-G3hNACS60ZTgVifIA" alt="Fenerbahce vs PSG">
                <h3 onclick="navigateToArticle('fenerbahce-psg')">Fenerbahçe gặp PSG tại vòng bảng</h3>
                <p>Fenerbahçe đối đầu với nhà đương kim vô địch PSG vào ngày 30/09/2025 tại Istanbul.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['inter-milan-man-united-2025']">
                <img src="https://i.ytimg.com/vi/6EuSyWhuPvc/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLDGllPAo8qtLK3npihOx6vE6L3lWQ" alt="Inter Milan vs Man United">
                <h3 onclick="navigateToArticle('inter-milan-man-united')">Inter Milan chạm trán Manchester United</h3>
                <p>Inter Milan sẽ đối đầu Manchester United vào ngày 30/09/2025 tại San Siro.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['tottenham-bayern-2025']">
                <img src="https://daknong.1cdn.vn/2024/08/01/assets-fr.imgfoot.com-media-cache-642x382-_fc-bayern-2324-6620360f924f1.jpg" alt="Tottenham vs Bayern Munich">
                <h3 onclick="navigateToArticle('tottenham-bayern')">Tottenham chiến Hùm Xám tại London</h3>
                <p>Trận đấu giữa Tottenham và Bayern Munich dự kiến vào ngày 01/10/2025 tại Tottenham Hotspur Stadium.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['chelsea-real-madrid-2025']">
                <img src="https://static-images.vnncdn.net/files/publish/2023/4/12/so-sanh-real-madrid-vs-chelsea-chu-nha-ap-dao-786.jpg?width=0&s=mVlNTGCbT_TG37QIJJQfaA" alt="Chelsea vs Real Madrid">
                <h3 onclick="navigateToArticle('chelsea-real-madrid')">Chelsea gặp Real Madrid tại Stamford Bridge</h3>
                <p>Chelsea sẽ tiếp Real Madrid vào ngày 01/10/2025 trong khuôn khổ vòng bảng.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['ajax-liverpool-2025']">
                <img src="https://media-cdn-v2.laodong.vn/storage/newsportal/2020/10/21/847314/Ajax-Vs-Liverpool.jpg?w=526&h=314&crop=auto&scale=both" alt="Ajax vs Liverpool">
                <h3 onclick="navigateToArticle('ajax-liverpool')">Ajax đối đầu Liverpool tại Amsterdam</h3>
                <p>Trận đấu giữa Ajax và Liverpool dự kiến vào ngày 21/10/2025 tại Johan Cruyff Arena.</p>
            </div>
        `;
    } else if (category ===
 'premier') {
        title = 'Premier League';
        scheduleText = `
            <h3>Lịch Thi Đấu 2025</h3>
            <p class="timestamp">Cập nhật: 06:44 AM, 10/05/2025</p>
            <div class="match-list">
                <div class="match-item">
                    <span class="date">10/05/2025</span>
                    <span class="team">Arsenal </span>
                    <span class="vs">vs</span>
                    <span class="team"> Bournemouth </span>
                </div>
                <div class="match-item">
                    <span class="date">11/05/2025</span>
                    <span class="team">Liverpool </span>
                    <span class="vs">vs</span>
                    <span class="team"> Tottenham </span>
                </div>
                <div class="match-item">
                    <span class="date">11/05/2025</span>
                    <span class="team">Manchester City </span>
                    <span class="vs">vs</span>
                    <span class="team"> West Ham </span>
                </div>
                <div class="match-item">
                    <span class="date">11/05/2025</span>
                    <span class="team">Chelsea </span>
                    <span class="vs">vs</span>
                    <span class="team"> Newcastle </span>
                </div>
                <div class="match-item">
                    <span class="date">17/05/2025</span>
                    <span class="team">Manchester United </span>
                    <span class="vs">vs</span>
                    <span class="team"> Everton </span>
                </div>
                <div class="match-item">
                    <span class="date">17/05/2025</span>
                    <span class="team">Fulham </span>
                    <span class="vs">vs</span>
                    <span class="team"> Liverpool </span>
                </div>
                <div class="match-item">
                    <span class="date">18/05/2025</span>
                    <span class="team">Tottenham </span>
                    <span class="vs">vs</span>
                    <span class="team"> Crystal Palace </span>
                </div>
                <div class="match-item">
                    <span class="date">18/05/2025</span>
                    <span class="team">West Ham </span>
                    <span class="vs">vs</span>
                    <span class="team"> Arsenal </span>
                </div>
                <div class="match-item">
                    <span class="date">24/05/2025</span>
                    <span class="team">Newcastle </span>
                    <span class="vs">vs</span>
                    <span class="team"> Manchester City </span>
                </div>
                <div class="match-item">
                    <span class="date">24/05/2025</span>
                    <span class="team">Everton </span>
                    <span class="vs">vs</span>
                    <span class="team"> Chelsea </span>
                </div>
                <div class="match-item">
                    <span class="date">25/05/2025</span>
                    <span class="team">Arsenal </span>
                    <span class="vs">vs</span>
                    <span class="team"> Liverpool </span>
                </div>
                <div class="match-item">
                    <span class="date">25/05/2025</span>
                    <span class="team">Manchester United </span>
                    <span class="vs">vs</span>
                    <span class="team"> Tottenham </span>
                </div>
                <div class="match-item">
                    <span class="date">25/05/2025</span>
                    <span class="team">Crystal Palace </span>
                    <span class="vs">vs</span>
                    <span class="team"> Fulham </span>
                </div>
                <div class="match-item">
                    <span class="date">25/05/2025</span>
                    <span class="team">West Ham </span>
                    <span class="vs">vs</span>
                    <span class="team"> Newcastle </span>
                </div>
                <div class="match-item">
                    <span class="date">25/05/2025</span>
                    <span class="team">Bournemouth </span>
                    <span class="vs">vs</span>
                    <span class="team"> Everton </span>
                </div>
                <div class="match-item">
                    <span class="date">25/05/2025</span>
                    <span class="team">Chelsea </span>
                    <span class="vs">vs</span>
                    <span class="team"> Manchester City </span>
                </div>
                <div class="match-item">
                    <span class="date">25/05/2025</span>
                    <span class="team">Aston Villa </span>
                    <span class="vs">vs</span>
                    <span class="team"> Brighton </span>
                </div>
            </div>
        `;
        articles = `
            <div class="article" onclick="window.location.href=matchUrls['arsenal-bournemouth-2025']">
                <img src="https://media.vov.vn/sites/default/files/styles/large/public/2025-05/arsenal_dau_voi_bournemouth.jpg" alt="Arsenal vs Bournemouth">
                <h3 onclick="navigateToArticle('arsenal-bournemouth')">Arsenal cần chiến thắng để giữ top 5</h3>
                <p>Arsenal đối mặt Bournemouth vào ngày 10/05/2025 tại Emirates Stadium, quyết tâm giành 3 điểm để đảm bảo vị trí trong top 5.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['liverpool-tottenham-2025']">
                <img src="https://theanalyst.com/wp-content/uploads/2025/04/liverpool-vs-spurs-preview.jpg" alt="Liverpool vs Tottenham">
                <h3 onclick="navigateToArticle('liverpool-tottenham')">Liverpool chạm trán Tottenham tại Anfield</h3>
                <p>Liverpool đối đầu Tottenham vào ngày 11/05/2025, một trận đấu quan trọng để duy trì vị trí dẫn đầu.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['manchester-city-west-ham-2025']">
                <img src="https://media.baovanhoa.vn/zoom/1000/Uploaded/ngoctrung/2024_08_31/doi-hinh-du-kien-west-ham-v-man-city_YFVL.png" alt="Man City vs West Ham">
                <h3 onclick="navigateToArticle('manchester-city-west-ham')">Manchester City gặp West Ham tại Etihad</h3>
                <p>Manchester City sẽ tiếp West Ham vào ngày 11/05/2025, với mục tiêu giành chiến thắng để cạnh tranh vị trí top 4.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['chelsea-newcastle-2025']">
                <img src="https://cms-sportsdunia-prod.s3.ap-southeast-2.amazonaws.com/cms-post/Preview%20%26%20Prediction%20%2822%29-1746535260683.jpg" alt="Chelsea vs Newcastle">
                <h3 onclick="navigateToArticle('chelsea-newcastle')">Chelsea đối đầu Newcastle tại Stamford Bridge</h3>
                <p>Chelsea gặp Newcastle vào ngày 11/05/2025, cả hai đội đều muốn giành điểm để cải thiện vị trí trên bảng xếp hạng.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['man-united-everton-2025']">
                <img src="https://wp.clutchpoints.com/wp-content/uploads/2025/02/Everton-vs.-Manchester-United-prediction-odds-pick.jpg?w=1200" alt="Man United vs Everton">
                <h3 onclick="navigateToArticle('man-united-everton')">Manchester United chạm trán Everton tại Old Trafford</h3>
                <p>Manchester United đối đầu Everton vào ngày 17/05/2025, một trận đấu quan trọng cho mục tiêu top 5.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['fulham-liverpool-2025']">
                <img src="https://vcdn1-thethao.vnecdn.net/2025/04/06/liverpool-fulham-1743950610-17-8059-6995-1743950744.jpg?w=460&h=0&q=100&dpr=2&fit=crop&s=jxpml5aUOZFcsyrlbL0qYw" alt="Fulham vs Liverpool">
                <h3 onclick="navigateToArticle('fulham-liverpool')">Fulham gặp Liverpool tại Craven Cottage</h3>
                <p>Fulham sẽ đối đầu với nhà vô địch Liverpool vào ngày 17/05/2025, hứa hẹn một trận đấu căng thẳng.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['tottenham-crystal-palace-2025']">
                <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2023/10/26/nhan-dinh-bong-da-hom-nay-crystal-palace-vs-tottenham-16983385779421317122159.jpg" alt="Tottenham vs Crystal Palace">
                <h3 onclick="navigateToArticle('tottenham-crystal-palace')">Tottenham đối đầu Crystal Palace tại London</h3>
                <p>Tottenham gặp Crystal Palace vào ngày 18/05/2025, với mục tiêu giành điểm để đảm bảo suất dự Europa League.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['west-ham-arsenal-2025']">
                <img src="https://images2.minutemediacdn.com/image/upload/c_crop,x_0,y_217,w_4584,h_2578/c_fill,w_720,ar_16:9,f_auto,q_auto,g_auto/images/GettyImages/mmsport/209/01jdvsz9qfhhneh08xr8.jpg" alt="West Ham vs Arsenal">
                <h3 onclick="navigateToArticle('west-ham-arsenal')">West Ham chạm trán Arsenal tại London Stadium</h3>
                <p>West Ham đối đầu Arsenal vào ngày 18/05/2025, một trận derby London đầy kịch tính.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['newcastle-man-city-2025']">
                <img src="https://i.ex-cdn.com/nongnghiepmoitruong.vn/files/content/2023/09/27/man-112043_250.jpeg" alt="Newcastle vs Man City">
                <h3 onclick="navigateToArticle('newcastle-man-city')">Newcastle gặp Manchester City tại St James' Park</h3>
                <p>Newcastle đối đầu Manchester City vào ngày 24/05/2025, cả hai đội đều cần điểm để đạt mục tiêu mùa giải.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['everton-chelsea-2025']">
                <img src="https://file3.qdnd.vn/data/images/0/2022/08/07/hieu_tv/chelsea%203.jpg" alt="Everton vs Chelsea">
                <h3 onclick="navigateToArticle('everton-chelsea')">Everton chạm trán Chelsea tại Goodison Park</h3>
                <p>Everton gặp Chelsea vào ngày 24/05/2025, một trận đấu quan trọng cho cả hai đội.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['arsenal-liverpool-2025']">
                <img src="https://thethaovanhoa.mediacdn.vn/372676912336973824/2024/10/26/arsenal-vs-liverpool-17299301903521825558707.jpg" alt="Arsenal vs Liverpool">
                <h3 onclick="navigateToArticle('arsenal-liverpool')">Arsenal đối đầu Liverpool tại Emirates</h3>
                <p>Trận đấu giữa Arsenal và Liverpool vào ngày 25/05/2025 tại Emirates Stadium, quyết định ngôi vương Premier League.</p>
            </div>
        `;
    } else if (category === 'fa') {
        title = 'FA Cup';
        scheduleText = `
            <h3>Lịch Thi Đấu 2025</h3>
            <p class="timestamp">Cập nhật: 06:44 AM, 10/05/2025</p>
            <div class="match-list">
                <div class="match-item">
                    <span class="date">17/05/2025</span>
                    <span class="team">Manchester City </span>
                    <span class="vs">vs</span>
                    <span class="team"> Crystal Palace </span>
                </div>
                <div class="match-item">
                    <span class="date">29/03/2025</span>
                    <span class="team">Liverpool </span>
                    <span class="vs">vs</span>
                    <span class="team"> Tottenham </span>
                </div>
                <div class="match-item">
                    <span class="date">29/03/2025</span>
                    <span class="team">Chelsea </span>
                    <span class="vs">vs</span>
                    <span class="team"> Newcastle </span>
                </div>
                <div class="match-item">
                    <span class="date">30/03/2025</span>
                    <span class="team">Manchester United </span>
                    <span class="vs">vs</span>
                    <span class="team"> Fulham </span>
                </div>
                <div class="match-item">
                    <span class="date">30/03/2025</span>
                    <span class="team">Arsenal </span>
                    <span class="vs">vs</span>
                    <span class="team"> West Ham </span>
                </div>
                <div class="match-item">
                    <span class="date">26/04/2025</span>
                    <span class="team">Liverpool </span>
                    <span class="vs">vs</span>
                    <span class="team"> Chelsea </span>
                </div>
                <div class="match-item">
                    <span class="date">26/04/2025</span>
                    <span class="team">Manchester United </span>
                    <span class="vs">vs</span>
                    <span class="team"> Crystal Palace </span>
                </div>
                <div class="match-item">
                    <span class="date">08/03/2025</span>
                    <span class="team">Brighton </span>
                    <span class="vs">vs</span>
                    <span class="team"> Aston Villa </span>
                </div>
                <div class="match-item">
                    <span class="date">08/03/2025</span>
                    <span class="team">Everton </span>
                    <span class="vs">vs</span>
                    <span class="team"> Bournemouth </span>
                </div>
                <div class="match-item">
                    <span class="date">09/03/2025</span>
                    <span class="team">Sheffield United </span>
                    <span class="vs">vs</span>
                    <span class="team"> Leeds United </span>
                </div>
                <div class="match-item">
                    <span class="date">09/03/2025</span>
                    <span class="team">Nottingham Forest </span>
                    <span class="vs">vs</span>
                    <span class="team"> Crystal Palace </span>
                </div>
            </div>
        `;
        articles = `
            <div class="article" onclick="window.location.href=matchUrls['man-city-crystal-palace-2025']">
                <img src="https://media-cdn-v2.laodong.vn/Storage/NewsPortal/2022/8/27/1086012/0D37818B-07B5-487A-9.jpeg" alt="Man City vs Crystal Palace">
                <h3 onclick="navigateToArticle('man-city-crystal-palace')">Manchester City vô địch FA Cup 2024/25</h3>
                <p>Manchester City đánh bại Crystal Palace 2-1 trong trận chung kết FA Cup vào ngày 17/05/2025 tại Wembley Stadium.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['liverpool-tottenham-fa-2025']">
                <img src="https://media.vov.vn/sites/default/files/styles/front_medium/public/2025-04/liverpool_dau_voi_tottenham.jpg" alt="Liverpool vs Tottenham">
                <h3 onclick="navigateToArticle('liverpool-tottenham-fa')">Liverpool đối đầu Tottenham tại tứ kết</h3>
                <p>Liverpool gặp Tottenham vào ngày 29/03/2025 trong khuôn khổ tứ kết FA Cup 2024/25 tại Anfield, hứa hẹn một trận đấu căng thẳng.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['chelsea-newcastle-fa-2025']">
                <img src="https://cdn-img.thethao247.vn/storage/files/ctvqt/2024/10/25/chelsea-vs-newcastle-prediction-1-185005avatar.jpg" alt="Chelsea vs Newcastle">
                <h3 onclick="navigateToArticle('chelsea-newcastle-fa')">Chelsea chạm trán Newcastle tại tứ kết</h3>
                <p>Chelsea đối đầu Newcastle vào ngày 29/03/2025 tại Stamford Bridge trong khuôn khổ tứ kết FA Cup, cả hai đội đều quyết tâm tiến xa.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['man-united-fulham-2025']">
                <img src="https://i.ytimg.com/vi/51WDzx7UvIE/maxresdefault.jpg" alt="Man United vs Fulham">
                <h3 onclick="navigateToArticle('man-united-fulham')">Manchester United gặp Fulham tại tứ kết</h3>
                <p>Manchester United đối đầu Fulham vào ngày 30/03/2025 tại Old Trafford, một trận đấu quan trọng để tiến vào bán kết FA Cup.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['arsenal-west-ham-2025']">
                <img src="https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/trossard-west-ham_0_iwzfnpj7.png?h=6dff888f&auto=webp&itok=xT-PnJmD" alt="Arsenal vs West Ham">
                <h3 onclick="navigateToArticle('arsenal-west-ham')">Arsenal chạm trán West Ham tại tứ kết</h3>
                <p>Arsenal đối đầu West Ham vào ngày 30/03/2025 tại Emirates Stadium, cả hai đội đều muốn giành vé vào bán kết FA Cup.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['liverpool-chelsea-fa-2025']">
                <img src="https://cdn.bongdaplus.vn/Assets/Media/2025/05/03/70/chelsea-vs-liverpool-nhan-dinh-680.jpg" alt="Liverpool vs Chelsea">
                <h3 onclick="navigateToArticle('liverpool-chelsea-fa')">Liverpool gặp Chelsea tại bán kết</h3>
                <p>Liverpool đối đầu Chelsea vào ngày 26/04/2025 tại Wembley, một trận bán kết FA Cup đầy kịch tính giữa hai đội bóng hàng đầu.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['man-united-crystal-palace-2025']">
                <img src="https://laodongthudo.vn/stores/news_dataimages/2025/022025/01/21/manchester-united-crystal-palace-match-preview-prediction-1024x57620250201213910.jpg" alt="Man United vs Crystal Palace">
                <h3 onclick="navigateToArticle('man-united-crystal-palace')">Manchester United chạm trán Crystal Palace tại bán kết</h3>
                <p>Manchester United gặp Crystal Palace vào ngày 26/04/2025 tại Wembley, quyết tâm giành vé vào chung kết FA Cup.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['brighton-aston-villa-2025']">
                <img src="https://cdn.bongdaplus.vn/Assets/Media/2025/03/31/8/Brighton-vs-Aston-Villa-nhan-dinh.jpg" alt="Brighton vs Aston Villa">
                <h3 onclick="navigateToArticle('brighton-aston-villa')">Brighton đối đầu Aston Villa tại vòng 5</h3>
                <p>Brighton gặp Aston Villa vào ngày 08/03/2025 trong khuôn khổ vòng 5 FA Cup, cả hai đội đều muốn tiến vào tứ kết.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['everton-bournemouth-2025']">
                <img src="https://i.ex-cdn.com/nongnghiepmoitruong.vn/files/content/2025/02/08/nhan-dinh-truc-tiep-everton-dau-voi-bournemouth-22h-ngay-8-2-165709_862-175633.jpg" alt="Everton vs Bournemouth">
                <h3 onclick="navigateToArticle('everton-bournemouth')">Everton chạm trán Bournemouth tại vòng 5</h3>
                <p>Everton đối đầu Bournemouth vào ngày 08/03/2025 tại Goodison Park trong khuôn khổ vòng 5 FA Cup.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['sheffield-leeds-2025']">
                <img src="https://cdn.bongdaplus.vn/Assets/Media/2025/02/22/8/sheffield-united-vs-leeds-nhan-dinh.jpg" alt="Sheffield United vs Leeds United">
                <h3 onclick="navigateToArticle('sheffield-leeds')">Sheffield United gặp Leeds United tại vòng 5</h3>
                <p>Sheffield United đối đầu Leeds United vào ngày 09/03/2025 tại Bramall Lane, một trận derby Yorkshire đầy hấp dẫn.</p>
            </div>
            <div class="article" onclick="window.location.href=matchUrls['nottingham-crystal-palace-2025']">
                <img src="https://bna.1cdn.vn/2025/05/03/images.actionnetwork.com-blog-2023-05-_crystal-palace.jpg" alt="Nottingham Forest vs Crystal Palace">
                <h3 onclick="navigateToArticle('nottingham-crystal-palace')">Nottingham Forest chạm trán Crystal Palace tại vòng 5</h3>
                <p>Nottingham Forest gặp Crystal Palace vào ngày 09/03/2025 tại City Ground, cả hai đội đều muốn tiến xa.</p>
            </div>
        `;
    }

    document.getElementById('category-title').textContent = title;
    document.getElementById('schedule-content').innerHTML = scheduleText + '<div class="articles">' + articles + '</div>';
    history.pushState({ category: category }, title, `?category=${category}`);
}

function navigateToArticle(articleId) {
    if (matchUrls && matchUrls[articleId + '-2025']) {
        window.location.href = matchUrls[articleId + '-2025'];
    } else if (matchUrls && matchUrls[articleId + '-fa-2025']) {
        window.location.href = matchUrls[articleId + '-fa-2025'];
    } else if (matchUrls && matchUrls[articleId + '-2026']) {
        window.location.href = matchUrls[articleId + '-2026'];
    } else {
        let content = '<div class="article-detail"><h2>Bài viết chưa có nội dung</h2><p>Vui lòng chọn một bài viết khác.</p></div>';
        document.getElementById('schedule-content').innerHTML = content;
        history.pushState({ articleId: articleId }, document.title, `?article=${articleId}`);
    }
}

function navigateToDetails(detailId) {
    let content;
    if (detailId === 'highlights') {
        content = `
            <div class="article-detail">
                <h2>Quan tâm nhất</h2>
                <p class="timestamp">Cập nhật: 06:44 AM, 10/05/2025</p>
                <p>Danh sách các trận đấu nổi bật được nhiều người hâm mộ quan tâm nhất trong thời gian tới:</p>
                <div class="highlight-list">
                    <div class="highlight-item">
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Brazil" alt="Brazil Logo" class="logo">
                        <div class="teams">
                            <span class="team-name">Brazil</span>
                            <span class="score">-</span>
                            <span class="team-name">Argentina</span>
                        </div>
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Argentina" alt="Argentina Logo" class="logo">
                        <span class="match-info">10/05/2025 - Giao hữu Quốc tế</span>
                    </div>
                    <div class="highlight-item">
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Liverpool" alt="Liverpool Logo" class="logo">
                        <div class="teams">
                            <span class="team-name">Liverpool</span>
                            <span class="score">-</span>
                            <span class="team-name">Tottenham</span>
                        </div>
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Tottenham" alt="Tottenham Logo" class="logo">
                        <span class="match-info">11/05/2025 - Premier League</span>
                    </div>
                    <div class="highlight-item">
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Man+City" alt="Man City Logo" class="logo">
                        <div class="teams">
                            <span class="team-name">Man City</span>
                            <span class="score">2-1</span>
                            <span class="team-name">Crystal Palace</span>
                        </div>
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Crystal+Palace" alt="Crystal Palace Logo" class="logo">
                        <span class="match-info">17/05/2025 - Chung kết FA Cup</span>
                    </div>
                    <div class="highlight-item">
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Man+City" alt="Man City Logo" class="logo">
                        <div class="teams">
                            <span class="team-name">Man City</span>
                            <span class="score">-</span>
                            <span class="team-name">Ajax</span>
                        </div>
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Ajax" alt="Ajax Logo" class="logo">
                        <span class="match-info">16/09/2025 - UEFA Champions League</span>
                    </div>
                    <div class="highlight-item">
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Arsenal" alt="Arsenal Logo" class="logo">
                        <div class="teams">
                            <span class="team-name">Arsenal</span>
                            <span class="score">-</span>
                            <span class="team-name">Liverpool</span>
                        </div>
                        <img src="https://via.placeholder.com/40/2F4F4F/FFFFFF?text=Liverpool" alt="Liverpool Logo" class="logo">
                        <span class="match-info">25/05/2025 - Premier League</span>
                    </div>
                </div>
                <div class="expected-matches">
                    <h3>Các trận đấu được mong chờ</h3>
                    <div class="expected-match">
                        <img src="https://via.placeholder.com/80x50/2F4F4F/FFFFFF?text=Arsenal+vs+Liverpool" alt="Arsenal vs Liverpool">
                        <p>25/05/2025: Arsenal vs Liverpool - Trận đấu quyết định ngôi vương Premier League</p>
                    </div>
                    <div class="expected-match">
                        <img src="https://via.placeholder.com/80x50/2F4F4F/FFFFFF?text=Chelsea+vs+Man+City" alt="Chelsea vs Man City">
                        <p>25/05/2025: Chelsea vs Manchester City - Cuộc chiến giành suất dự Champions League</p>
                    </div>
                    <div class="expected-match">
                        <img src="https://via.placeholder.com/80x50/2F4F4F/FFFFFF?text=Bayern+vs+Real+Madrid" alt="Bayern vs Real Madrid">
                        <p>05/11/2025: Bayern Munich vs Real Madrid - Đại chiến tại UEFA Champions League</p>
                    </div>
                </div>
            </div>
        `;
    } else {
        content = '<div class="article-detail"><h2>Chi tiết chưa có nội dung</h2><p>Vui lòng chọn một mục khác.</p></div>';
    }
    document.getElementById('schedule-content').innerHTML = content;
    history.pushState({ detailId: detailId }, document.title, `?detail=${detailId}`);
}

// Xử lý sự kiện popstate để quay lại lịch sử
window.onpopstate = function(event) {
    if (event.state) {
        if (event.state.category) {
            showContent(event.state.category);
        } else if (event.state.articleId) {
            navigateToArticle(event.state.articleId);
        } else if (event.state.detailId) {
            navigateToDetails(event.state.detailId);
        }
    }
};

// Hiển thị nội dung mặc định khi trang tải
window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category');
    const article = urlParams.get('article');
    const detail = urlParams.get('detail');

    if (category) {
        showContent(category);
    } else if (article) {
        navigateToArticle(article);
    } else if (detail) {
        navigateToDetails(detail);
    } else {
        showContent('friendly');
    }
};

// Chỉ gán sự kiện click cho các link có data-category (sidebar)
document.querySelectorAll('nav a[data-category]').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const category = this.getAttribute('data-category');
        if (category) {
            showContent(category);
        }
    });
});

// Sử dụng event delegation để xử lý sự kiện click trên các bài viết
document.getElementById('schedule-content').addEventListener('click', function(e) {
    const target = e.target.closest('.article h3');
    if (target) {
        e.preventDefault();
        const articleId = target.getAttribute('onclick').replace("navigateToArticle('", "").replace("')", "");
        navigateToArticle(articleId);
    }
});

// Thêm sự kiện click cho sidebar
document.querySelectorAll('.sidebar-item p').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const detailId = this.getAttribute('onclick').replace("navigateToDetails('", "").replace("')", "");
        navigateToDetails(detailId);
    });
});
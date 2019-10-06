$(window).load(init());

function init() {
    $("#startBtn").click(function(){
        var keyword = $("#keyword").val();
        if (keyword == ""){
            alert("キーワードが空です。");
        }else{
            window.location.href = "/scraping/" + keyword;
        }
    });
}
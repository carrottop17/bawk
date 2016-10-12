$(function() {
  $('.marquee').marquee({
    duration: 5000,
    startVisible: true,
    duplicated: true
  });
});

$(document).ready(function(){
	$('.vote').click(function(){
		var vid = $(this).attr('postid')
		if($(this).hasClass("vote-up")){
			var voteType = 1;
		}else{
			var voteType = -1;
		}
		$.ajax({
			url:"/process_vote",
			type: "post",
			data: {vid:vid, voteType:voteType},
			success: function(result){
				if(result.message == 'voteChanged'){
					$("div[up-down-id='" + vid + "']").html(result.vote_total)
				}else if(result.message == 'alreadyVoted'){
					$("div[up-down-id='" + vid + "']").html('you have already voted on this buzz')
				}
				console.log(result)
			}

		})
	})
});


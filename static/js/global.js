$(document).ready(function(){
  $("form .required").bind("focus", function(e){
      $(this).css("background-color","#FFFFFF");
        });
});

function VerifyForm(form)
{
    var feedback = "";
    
    $("#" + form.id + " .required input").each(function(i){
        if(this.value == "")
        {
            $(this).css("background-color","#FFFF00");
            
            feedback += "-- " + this.title + "\n";
        }
        });
        
     if(feedback == "")
     {
        return true;
     }
     else
     {
        alert("The following fields are required:\n\n" + feedback);
     }
     
     return false;
}

function PostAjaxForm(form, render_callback, validate)
{
	//Validate the form before making an AJAX call
	if(validate && !VerifyForm(form))
		return false;
	
    var url = $(form).attr("action");
	var data = new Object;
	
	//Build a collection of all valid post values
	$(form).find(":input").not(":submit, :checkbox").each(function(i)
	{
		if ($(this).attr("name") != undefined) {
			data[this.name] = $(this).val();
		}
	})
	
	$(form).find(":checked").each(function(i)
	{
		if ($(this).attr("name") != undefined) {
			data[this.name] = $(this).val();
		}
	})
	
	//Perform POST AJAX request
	$.post(url, data, render_callback);
     
	return false;
}

function LoadHTMLAfterFormPost(form, container, post_render_callback)
{	
    var url = $(form).attr("action");
	var data = new Object;
	
	//Build a collection of all valid post values
	$(form).find(":input").not(":submit, :checkbox").each(function(i)
	{
		if ($(this).attr("name") != undefined) {
			data[this.name] = $(this).val();
		}
	})
	
	$(form).find(":checked").each(function(i)
	{
		if ($(this).attr("name") != undefined) {
			data[this.name] = $(this).val();
		}
	})
	
	//Perform POST AJAX request
	container.load(url, data, post_render_callback);
     
	return false;
}

function ToggleFeedEdit(feed_id)
{
	$(".feed-edit-fields." + feed_id).slideToggle("slow");
}

function FeedDelete(feed_id)
{
	$("#FeedEditFormFeedID").val(feed_id);
	$("#FeedEditFormAction").val("feed_delete");
	$("#FeedEditFormFeedName").val("");
	$("#FeedEditForm").submit();
}

function FeedEdit(feed_id)
{
	$("#FeedEditFormFeedID").val(feed_id);
	$("#FeedEditFormAction").val("feed_edit");
	$("#FeedEditFormFeedName").val($("#feedName" + feed_id).val());
	$("#FeedEditForm").submit();
}



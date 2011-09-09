function get_values(source, target, url) {       
        var obj = {csrfmiddlewaretoken: getCookie('csrftoken')};
        obj[$(source).attr('name')] = $(source).val();
        $.post(url, obj,
                function(data){
					$(target).html("");//clear old options
					data = eval(data);//get json array
					for (i = 0; i < data.length; i++)//iterate over all options
					{
					  for ( key in data[i] )//get key => value
					  {	
							$(target).get(0).add(new Option(data[i][key],[key]), document.all ? i : null);
                      }
					}
					$("option:first", target).attr( "selected", "selected" );//select first option
},
                'json'
                );
}

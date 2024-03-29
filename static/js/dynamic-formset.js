function updateElementIndex(el, prefix, ndx) {
		var id_regex = new RegExp('(' + prefix + '-\\d+)');
		var replacement = prefix + '-' + ndx;
		if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
		if (el.id) el.id = el.id.replace(id_regex, replacement);
		if (el.name) el.name = el.name.replace(id_regex, replacement);
	}

    function addForm(btn, prefix) {
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        var row = $('.dynamic-form:first.' + prefix).clone(true).get(0);
        $(row).removeAttr('id').insertAfter($('.dynamic-form:last.' + prefix)).children('.hidden').removeClass('hidden');
        $(row).children().not(':last').children().each(function() {
    	    updateElementIndex(this, prefix, formCount);
    	    $(this).val('');
        });
        $(row).find('.delete-row').click(function() {
    	    deleteForm(this, prefix);
        });
        $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
        
        var input_calendar = "id_" + prefix + "-" + formCount + "-datetime";
        var icon_calendar = "id_" + prefix + "-" + formCount + "-datetime_trigger";
        if( document.getElementById( icon_calendar ))
            generationCalendar( input_calendar , icon_calendar, formCount, prefix );
        
        return false;
    }

    function deleteForm(btn, prefix) {
        $(btn).parents('.dynamic-form').remove();
        var forms = $('.dynamic-form.' + prefix);
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
    	    $(forms.get(i)).children().not(':last').children().each(function() {
    	        updateElementIndex(this, prefix, i);
    	    });
        }
        return false;
    }
    function generationCalendar( el_input, el_img, formCount, prefix ){
        var obj = "id_" + prefix + "_" + formCount + "_datetime_cal" ;
        obj  = new Calendar({
              inputField: el_input,
              dateFormat: "%Y-%m-%d %H:%M",
              trigger: el_img,
              showTime: 24,
              onSelect   : function() { this.hide() }
      });
    }


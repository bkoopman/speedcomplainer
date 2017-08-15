function setColor(name, inverse) {
	var value = $(name).val();
	var max = $(name).attr("data-max");

	switch (true) {
		case (value < max/3):
			if (inverse) {
				// green
				$(name).trigger("configure", {"fgColor":"#2dbf12", "inputColor":"#2dbf12"});
			} else {
				// orange
				$(name).trigger("configure", {"fgColor":"#f79727", "inputColor":"#f79727"});
			}
			break;
		case (value < max/1.5):
			// yellow
			$(name).trigger("configure", {"fgColor":"#ffff33", "inputColor":"#ffff33"});
			break;
		default:
			if (inverse) {
				// orange
				$(name).trigger("configure", {"fgColor":"#f79727", "inputColor":"#f79727"});
			} else {
				// green
				$(name).trigger("configure", {"fgColor":"#2dbf12", "inputColor":"#2dbf12"});
			}
	}
}
$(function() {
	$(".dial").knob().trigger(
		"configure",
		{
			"width":200,
			"bgColor":"#355064",
			"angleOffset":-125,
			"angleArc":250,
			"step":.01,
			"thickness":.2
		}
		);
	setColor("#ping", true);
	setColor("#download");
	setColor("#upload");
});
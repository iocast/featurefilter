var IE = document.all?true:false
if (!IE) document.captureEvents(Event.MOUSEMOVE)

document.onmousemove = getMouseXY;
var mouseX = 0;
var mouseY = 0;

function getMouseXY(evt) {
	if (IE) {
		mouseX = event.clientX + document.body.scrollLeft;
		mouseY = event.clientY + document.body.scrollTop;
	} else {
		mouseX = evt.pageX;
		mouseY = evt.pageY;
	}  
}

/**
 * Handels images and identifier for clickable features.
 */
var ImageHandler = Class.extend({
	images : [],
	symbolizer : null,
	addImage : function(tag, value, operator, url) {
		this.images.push({
			"tag" : tag,
			"value" : value,
			"operator" : operator,
			"url" : url
		});
	},
	setSymbolObject : function(symbolizer) {
		this.symbolizer = symbolizer;
		return this.refresh();
	},
	getCustomRules : function() {
		var style = new OpenLayers.Style();
		for(var i = 0; i < this.images.length; i++) {
			var rule = new OpenLayers.Rule({ 
				filter : new OpenLayers.Filter.Comparison({
					type : this.images[i]["operator"],
					property : this.images[i]["tag"],
					value : this.images[i]["value"],
				}),
				symbolizer : {pointRadius : 8, externalGraphic : this.images[i]["url"], graphicOpacity : 1, fillOpacity : 1}
			});
			style.addRules([rule]); 
		}
		
		style.addRules([
			new OpenLayers.Rule({
				elseFilter : true,
				symbolizer : {pointRadius : 8, externalGraphic : this.symbolizer.getElseSymbol(), graphicOpacity : 1, fillOpacity : 1}
			})
		]);
		
		return style;
	},
	refresh : function() {
		var ret = false;
		var symbols = this.symbolizer.getSymbols();
		
		for(index in symbols) {
			if(this.images.length > 0) {
				var found = true;
				for(var i = 0; i < this.images.length; i++) {
					if(this.images[i]["tag"] == symbols[index][0] && this.images[i]["value"] == symbols[index][1]) {
						found = false;
						break;
					}
				}
				if(found) {
					this.addImage(symbols[index][0], symbols[index][1], symbols[index][2], symbols[index][3]);
					ret = true;
				}

			} else {
				this.addImage(symbols[index][0], symbols[index][1], symbols[index][2], symbols[index][3]);
				ret = true;
			}
		}
		
		return ret;
	}
});


/**
 * Feature Filter class
 * - handles most important functions
 */
var FeatureFilter = Class.extend({
	map : null,
	imageHandler : null,
	/**
	 * key defines the wfs-tag
	 */
	construct : function(map, imageHandler) {
		this.map = map;
		this.imageHandler = imageHandler;
		
		if(typeof this.map.tooltips === "undefined") {
			this.map.tooltips = new Array();
		}
		
	},
	addLayer : function(layer, html, footer, featureServer, typeName, idAttribute, clusterLabel, clusterDelimiter, clusterHTML, clusterAmount, navigation, clusterAmount) {
		if(typeof(layer.styleMap) != 'undefined') {
			layer.styleMap.styles = {"default" : this.imageHandler.getCustomRules()};
		}
		
		this.map.addLayer(layer);
		
		if(html.length > 0)
			this.addSelectControl(layer, html, footer, featureServer, typeName, idAttribute, clusterLabel, clusterDelimiter, clusterHTML, clusterAmount, navigation, clusterAmount);
	},
	removeLayer : function(id) {
		var layer;
		if((layer = this.map.getLayer(id)) != null)
			layer.destroy();
	},
	removeAllLayers : function() {
		var layers = this.map.getLayersByClass('OpenLayers.Layer.Vector');
		for(index in layers) {
			layers[index].destroy();
		}
	},
	getLayer : function(id) {
		return this.map.getLayer(id);
	},
	refreshStyleMaps : function() {
		layers = this.map.getLayersByClass('OpenLayers.Layer.Vector');
		for(index in layers) {
			if(typeof(layers[index].styleMap) != 'undefined') {
				layers[index].styleMap.styles = {"default" : this.imageHandler.getCustomRules()};
			}
		}
	},
	redrawLayers : function() {
		layers = this.map.getLayersByClass('OpenLayers.Layer.Vector');
		for(index in layers) {
			layers[index].redraw();
		}
	},
	addSelectControl : function(layer, html, footer, featureServer, typeName, idAttribute, clusterLabel, clusterDelimiter, clusterHTML, clusterAmount, navigation, clusterAmount) {
		/*
		var layers = [];
		for(key in this.map.layers) {
			if(this.map.layers[key] instanceof OpenLayers.Layer.WFSFilter)
				layers.push(this.map.layers[key]);
		}
		selectControl = new OpenLayers.Control.SelectFeature(layers, {*/
		selectControl = new OpenLayers.Control.SelectFeature([layer], {
			hover : false,
			toggle : true,
			highlightOnly: false,
			multiple : false,
			featureFilter : this,
			callbacks : {
				over : function(feature) {
					var regex = new RegExp(/\$\{([^}]+)\}/);
					var match = null;
					
					var tooltipDiv = document.createElement('div');
					style = document.createAttribute('style');
					style.nodeValue = 'z-index: 3000;position:absolute;left:'+(mouseX+10)+'px;top:'+(mouseY+10)+'px;background-color:#FFFFCC;border:1px solid #BBBBBB;padding:1px;';
					tooltipDiv.setAttributeNode(style);
					if(feature.attributes.name.length > 0) {
						tooltipDiv.innerHTML = (feature.attributes.name == "None") ? "<p>No Name</p>" :	"<p>"+feature.attributes.name+"</p>";
					} else {
						tooltipDiv.innerHTML = "<p>" + eval(regex.exec(clusterAmount)[1]) + " features in this cluster</p>";
					}
					document.body.appendChild(tooltipDiv);
					this.map.tooltips[feature.fid] = tooltipDiv;
				},
				out : function(feature) {
					if(feature.fid in this.map.tooltips) {
						document.body.removeChild(this.map.tooltips[feature.fid]);
						delete this.map.tooltips[feature.fid];
					}
				},
				click : function(feature) {
					if(feature.fid in this.map.tooltips) {
						document.body.removeChild(this.map.tooltips[feature.fid]);
						delete this.map.tooltips[feature.fid];
					}
					this.clickFeature(feature);
				}
			},
			onSelect: function(feature) {
				var regex = new RegExp(/\$\{([^}]+)\}/);
				var match = null;
				var output = html;
				var popup = null;
				var ids = [];
				
				try {
					ids = eval(regex.exec(clusterLabel)[1]).split(clusterDelimiter);
					ids.splice(0,1);
				} catch(err) {
				}
								
				if(ids.length > 0) {
					//feature is a cluster -> load addtional info
					var counter = 0;
					output = '<div class="ff_load_indicator">Loading...</div>';
					
					var filterencoding = "<Filter><Or>";
					for(index in ids) {
						counter++;
						filterencoding += "<PropertyIsEqualTo><PropertyName>" + idAttribute + "</PropertyName><Literal>" + ids[index] + "</Literal></PropertyIsEqualTo>";
						if(counter >= clusterAmount)
							break;
					}
					filterencoding += "</Or></Filter>";
					var request = OpenLayers.Request.GET({
						url : featureServer,
						async : true,
					    params: {
							service : "WFS",
							typename : typeName,
							request : "GetFeature",
							filter : filterencoding
						},
					    callback : function(request) {
					    	var oldFeature = feature;
							var features = new OpenLayers.Format.GML().read(request.responseText);
							output = "";
							if(features.length == 0) {
								output = '<div class="ff_warning">Coud not find any feature.</div>';
								return;
							}
							
							for(var i = 0; i < features.length; i++) {
								feature = features[i];
								if(typeof(clusterHTML) == "function") {
									output += clusterHTML(feature);
								} else {
									var featureHTML = clusterHTML;
									while((match = regex.exec(featureHTML)) != null) {
										featureHTML = featureHTML.replace(match[0], eval(match[1]));
									}
									output += featureHTML
								}
							}
							if(ids.length > clusterAmount) {
								output += "<p>...</p>";
							}
							
							if(typeof(navigation) == "function") {
								output += navigation(oldFeature);
							} else {
								output += navigation;
								while((match = regex.exec(output)) != null) {
									output = output.replace(match[0], eval(match[1]));
								}
							}
							
							output = "<div>" + output + "</div>";
							
							feature = oldFeature;
							
							if(feature.popup != null)
								feature.popup.setContentHTML(output);
						},
						failure : function(request) {
							if(request.status == 414) {
								// Request-URI Too Large
								output = '<div class="ff_info">Too many results, please zoom in.</div>';
							} else {
								// other error
								output = '<div class="ff_error">An unknonw error occured. Please try again later.</div>';
							}
							if(feature.popup != null)
								feature.popup.setContentHTML(output);
						}
					});
				} else {
					if(typeof(html) == "function") {
						output = html(feature);
					} else {
						while((match = regex.exec(output)) != null) {
							output = output.replace(match[0], eval(match[1]));
						}
					}
					
					if(typeof(footer) == "function") {
						output += footer(feature);
					} else {
						output += footer;
						while((match = regex.exec(output)) != null) {
							output = output.replace(match[0], eval(match[1]));
						}
					}
					output = "<div>" + output + "</div>";
				}
				
			    popup = new OpenLayers.Popup.FramedCloud("chicken", 
			                             feature.geometry.getBounds().getCenterLonLat(),
			                             null,
			                             output,
			                             null, true, function(event) {
			        selectControl.onUnselect(feature);
			    });
			    feature.popup = popup;
			    popup.feature = feature;
			    this.map.addPopup(popup);
			},
			onUnselect: function(feature) {
				if(feature.popup != null) {
					this.map.removePopup(feature.popup);
					feature.popup.destroy();
					feature.popup = null;
				}
			}
		});
		this.map.addControl(selectControl);
		selectControl.activate();
	},
	closeEverything : function() {
		for(var index in this.map.popups) {
			this.map.removePopup(this.map.popups[index]);
		}
		
		for(var key in this.map.tooltips) {
			document.body.removeChild(this.map.tooltips[key]);
			delete this.map.tooltips[key];
		}
	},
});

/**
 * map extension for Protocol layer
 */

OpenLayers.Protocol.WFSFilter = OpenLayers.Class(OpenLayers.Protocol.WFS.v1_1_0, {
	initialize : function() {
		OpenLayers.Protocol.WFS.v1_1_0.prototype.initialize.apply(this, arguments);
		/*
		if(typeof(this.beforeSend) == "function") {
			this.beforeSend();
		}
		*/
	},
	
	read: function(options) {
		this.beforeSend();
		
		OpenLayers.Protocol.WFS.v1_1_0.prototype.read.apply(this, arguments);
	},

    handleRead : function(response, options) {
		OpenLayers.Protocol.WFS.v1_1_0.prototype.handleRead.apply(this, arguments);
		
		switch(response.code) {
			case OpenLayers.Protocol.Response.FAILURE:
				if(typeof(this.onError) == "function") {
					this.onError();
				}
				break;
			case OpenLayers.Protocol.Response.SUCCESS:
				if(response.features == null) {
					if(typeof(this.noFeature) == "function") {
						this.noFeature();
					}
				} else if(typeof(this.onSuccess) == "function") {
					this.onSuccess(response.priv);
				}
				/*
				if(options.object) {
					options.object.redraw();
				}*/
				break;
		}
		
		if(typeof(this.afterReceive) == "function") {
			this.afterReceive();
		}
		
	},
	beforeSend : function() {},
	afterReceive : function() {},
	noFeature : function() {},
	onError : function(request, errors) {},
	onSuccess : function(request) {
		if(request.responseXML != null) {
			if(request.responseXML.firstChild.nodeName == 'ExceptionReport') {
				errors = {};
				for(var i = 0; i < request.responseXML.firstChild.childNodes.length; i++) {
					child = request.responseXML.firstChild.childNodes[i];
					if(child.nodeType == 1) {
						for(var a = 0; a < child.childNodes.length; a++) {
							element = child.childNodes[a];
							if(element.nodeType == 1) {
								if(element.nodeName == 'ExceptionText') {
									errors[child.getAttribute('exceptionCode')] = element.textContent;
								}
							}
						}
					}
					
				}
				/*
				if(typeof(this.callback) == "function") {
					this.callback(errors);
				}
				*/
				this.onError(request, errors);
			} else {
				if(request.responseXML.lastChild.childNodes.length > 1) {
					//OpenLayers.Layer.GML.prototype.requestSuccess.apply(this, arguments);
				} else {
					/*
					if(typeof(this.noFeature) == "function") {
						this.noFeature();
					}
					*/
				}
			}
		} else {
			//alert(request.responseText);
			this.onError(request, {});
		}
		/*
		if(typeof(this.afterReceive) == "function") {
			this.afterReceive();
		}
		*/
	}

});

/**
 * map extension for Vector layer
 */
OpenLayers.Layer.VectorFilter = OpenLayers.Class(OpenLayers.Layer.Vector, {
	initialize : function() {
		var id = arguments[0];
		var args = Array.prototype.slice.call(arguments);
		args.splice(0,1);
		OpenLayers.Layer.Vector.prototype.initialize.apply(this, args);
		
		this.id = id;
	}
});

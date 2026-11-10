package dev.gnomehollow.client;

import com.geckolib.model.*;
import com.geckolib.renderer.*;
import dev.gnomehollow.GnomeHollow;
import net.minecraft.client.renderer.entity.EntityRendererProvider;

/**
 * Model:      assets/gnomehollow/geckolib/models/entity/<naam>.geo.json
 * Animaties:  assets/gnomehollow/geckolib/animations/entity/<naam>.animation.json
 * Texture:    assets/gnomehollow/textures/entity/<naam>.png
 *
 * Bewust met "raw types": de generieke parameters van GeoEntityRenderer zijn tussen GeckoLib-versies
 * gewijzigd (5.5.2 verwijderde de "& GeoRenderState"-generic), zo blijft dit bij kleine updates werken.
 */
@SuppressWarnings({"rawtypes", "unchecked"})
public class GnomeRenderer extends GeoEntityRenderer {
	public GnomeRenderer(EntityRendererProvider.Context context, String assetName) {
		super(context, new DefaultedEntityGeoModel(GnomeHollow.id(assetName)));
	}
}

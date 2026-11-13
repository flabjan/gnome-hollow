package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.village.VillageInfo;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;

/** Een rondje langs de gemeenschappelijke plekken: de markt, de bibliotheek of de gemeenschappelijke tuin. */
public class VisitGoal extends ActivityGoal {
	private int kind;      // 0 markt, 1 bibliotheek, 2 tuin
	private BlockPos poi;

	public VisitGoal(GnomeEntity gnome) {
		super(gnome, 700);
	}

	@Override
	protected boolean allowed() {
		return this.gnome.hasVillage() && this.gnome.canLeisure();
	}

	@Override
	protected boolean choose(ServerLevel level) {
		var rnd = this.gnome.getRandom();
		if (!this.gnome.busyLeisureChance() || rnd.nextInt(2) != 0) return false;
		VillageInfo info = VillageInfo.get(level, this.gnome.villageCenter());
		List<Integer> kinds = new ArrayList<>();
		if (info.market != null) { kinds.add(0); if (this.gnome.favorite() == 4) { kinds.add(0); kinds.add(0); } }
		if (info.library != null) { kinds.add(1); if (this.gnome.favorite() == 2) { kinds.add(1); kinds.add(1); } }
		if (!info.gardens.isEmpty()) { kinds.add(2); if (this.gnome.favorite() == 1) { kinds.add(2); kinds.add(2); } }
		if (kinds.isEmpty()) return false;
		this.kind = kinds.get(rnd.nextInt(kinds.size()));
		this.poi = this.kind == 0 ? info.market : this.kind == 1 ? info.library : info.gardens.get(rnd.nextInt(info.gardens.size()));
		this.dest = GnomeUtil.findStandNear(level, this.poi).orElse(null);
		if (this.dest == null) return false;
		this.duration = 300 + rnd.nextInt(500);
		return true;
	}

	@Override
	protected void onArrive(ServerLevel level) {
		this.gnome.getLookControl().setLookAt(this.poi.getX() + 0.5, this.poi.getY() + 0.8, this.poi.getZ() + 0.5);
		if (this.kind == 2) this.gnome.startAnim("work");       // tuinieren
		else if (this.kind == 0) this.gnome.startAnim("talk");  // kletsen bij de kraam
	}

	@Override
	protected void during(ServerLevel level) {
		if (this.gnome.tickCount % 20 == 0) this.gnome.getLookControl().setLookAt(this.poi.getX() + 0.5, this.poi.getY() + 0.8, this.poi.getZ() + 0.5);
	}

	@Override
	protected void onEnd(ServerLevel level) {
		this.gnome.stopAnim();
	}
}

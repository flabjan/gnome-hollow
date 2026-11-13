package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.List;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.monster.Monster;

/** Na een gevecht: de healer zoekt gewonde gnomes (wachters eerst) op en geneest ze zodra het veilig is. */
public class HealerRoundsGoal extends ActivityGoal {
	private GnomeEntity patient;

	public HealerRoundsGoal(GnomeEntity gnome) {
		super(gnome, 60);
	}

	@Override
	protected boolean allowed() {
		return this.gnome.isAlive() && !this.gnome.inDanger() && this.gnome.getTarget() == null && !this.gnome.isTrading();
	}

	@Override
	protected int nextCooldown() {
		return 80;
	}

	@Override
	protected double speed() {
		return 0.9;
	}

	@Override
	protected double arriveDist() {
		return 2.8;
	}

	@Override
	protected boolean choose(ServerLevel level) {
		List<GnomeEntity> hurt = level.getEntitiesOfClass(GnomeEntity.class, this.gnome.getBoundingBox().inflate(28.0, 8.0, 28.0),
				g -> g != this.gnome && g.isAlive() && g.getHealth() < g.getMaxHealth() * 0.75F);
		GnomeEntity best = null;
		for (GnomeEntity g : hurt) {
			boolean safe = level.getEntitiesOfClass(Monster.class, g.getBoundingBox().inflate(12.0, 5.0, 12.0), m -> m.isAlive()).isEmpty();
			if (!safe) continue;
			if (best == null || (g.profession().isGuard() && !best.profession().isGuard())
					|| (g.profession().isGuard() == best.profession().isGuard() && g.getHealth() < best.getHealth())) best = g;
		}
		if (best == null) return false;
		this.patient = best;
		this.dest = best.blockPosition();
		this.duration = 140;
		return true;
	}

	@Override
	protected void refreshDest() {
		if (this.patient != null) this.dest = this.patient.blockPosition();
	}

	@Override
	protected void onArrive(ServerLevel level) {
		if (this.patient != null && this.patient.isAlive()) {
			this.gnome.getLookControl().setLookAt(this.patient, 30.0F, 30.0F);
			this.gnome.castHeal(level, this.patient);
		}
		this.ticks = Math.max(this.ticks, this.duration - 30);   // na het helen nog even blijven staan
	}

	@Override
	protected void onEnd(ServerLevel level) {
		this.patient = null;
		this.gnome.stopAnim();
	}
}

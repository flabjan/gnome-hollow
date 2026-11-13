package dev.gnomehollow.goal;

import dev.gnomehollow.GnomeConfig;
import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.entity.Profession;
import dev.gnomehollow.village.DayTracker;
import dev.gnomehollow.village.MusicSessions;
import dev.gnomehollow.village.VillageInfo;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;

/**
 * Spontane muziek zoals bij de Ribbits: soms begint een Nitwit een liedje, andere gnomes die toevallig niets te doen hebben
 * komen erbij staan (muzikanten spelen een eigen instrument, de rest luistert). Er is steeds maar één liedje per dorp, het
 * wordt helemaal afgespeeld, en werk in het eigen beroep gaat altijd voor.
 */
public class MusicGoal extends ActivityGoal {
	private final Performer performer = new Performer();
	private MusicSessions.Session session;
	private boolean listener;

	public MusicGoal(GnomeEntity gnome) {
		super(gnome, 600);
	}

	@Override
	protected boolean allowed() {
		if (!GnomeConfig.get().musicEnabled || !this.gnome.hasVillage() || !this.gnome.canLeisure()) return false;
		return this.session == null || this.gnome.level().getGameTime() < this.session.end;
	}

	@Override
	protected int nextCooldown() {
		return 600 + this.gnome.getRandom().nextInt(1200);
	}

	@Override
	protected boolean choose(ServerLevel level) {
		long key = this.gnome.villageCenter().asLong();
		var rnd = this.gnome.getRandom();
		MusicSessions.Session s = MusicSessions.get(level, key);
		if (s != null) {
			BlockPos sp = s.spot;
			if (this.gnome.distanceToSqr(sp.getX() + 0.5, sp.getY(), sp.getZ() + 0.5) > 26.0 * 26.0) return false;
			if (this.gnome.playsMusic()) {
				if (s.takenCount() >= MusicSessions.PARTS || rnd.nextInt(3) != 0) return false;
				this.listener = false;
			} else {
				if (rnd.nextInt(10) != 0 || !this.gnome.busyLeisureChance()) return false;
				this.listener = true;
			}
		} else {
			boolean nitwit = this.gnome.profession() == Profession.NITWIT;
			DayTracker.Phase ph = this.gnome.phase();
			if (!this.gnome.playsMusic() || !(nitwit || ph == DayTracker.Phase.LEISURE)) return false;
			double p = 0.004 * GnomeConfig.get().musicFrequency * (nitwit ? 1.0 : 0.4);
			if (rnd.nextDouble() > p) return false;
			VillageInfo info = VillageInfo.get(level, this.gnome.villageCenter());
			BlockPos meet = info.meetingSpot();
			BlockPos spot = this.gnome.distanceToSqr(meet.getX() + 0.5, meet.getY(), meet.getZ() + 0.5) < 24.0 * 24.0 ? meet : this.gnome.blockPosition();
			s = MusicSessions.create(level, key, spot, this.gnome.getId(),
					GnomeConfig.get().musicSessionMinSeconds * 20, GnomeConfig.get().musicSessionMaxSeconds * 20, rnd.nextInt(Songs.ALL.length));
			this.listener = false;
		}
		this.session = s;
		this.dest = GnomeUtil.ring(level, s.spot, this.gnome.getId(), this.listener ? 5.0 : 2.5);
		this.duration = (int) Math.max(40L, s.end - level.getGameTime() + 40L);
		return true;
	}

	@Override
	protected void onArrive(ServerLevel level) {
		if (!this.listener && !this.performer.tryJoin(this.gnome, this.session)) this.ticks = this.duration;
	}

	@Override
	protected void during(ServerLevel level) {
		BlockPos sp = this.session.spot;
		if (this.gnome.tickCount % 20 == 0) this.gnome.getLookControl().setLookAt(sp.getX() + 0.5, sp.getY() + 1.0, sp.getZ() + 0.5);
		if (this.listener) {
			if (this.gnome.getRandom().nextInt(400) == 0) this.gnome.oneShot("talk");
		} else if (!this.performer.play(level, this.gnome)) {
			this.ticks = this.duration;
		}
	}

	@Override
	protected void onEnd(ServerLevel level) {
		this.performer.leave(this.gnome);
		this.session = null;
		this.listener = false;
	}
}

package dev.gnomehollow.entity;

import com.geckolib.animatable.*;
import com.geckolib.animatable.instance.*;
import com.geckolib.animatable.manager.*;
import com.geckolib.animation.*;
import com.geckolib.animation.state.*;
import com.geckolib.util.*;
import dev.gnomehollow.GnomeConfig;
import dev.gnomehollow.GnomeTrades;
import dev.gnomehollow.ModSounds;
import dev.gnomehollow.goal.*;
import dev.gnomehollow.village.DayTracker;
import java.util.List;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.OpenDoorGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.trading.Merchant;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;

/**
 * Eén klasse voor alle gnomes; het beroep volgt uit het EntityType (gnome_healer, gnome_warrior, ...).
 * Persistente staat (thuis, dorp, vriend, voorkeuren, handelsseed, bekende spelers) wordt opgeslagen in de entity-NBT.
 */
public class GnomeEntity extends PathfinderMob implements GeoEntity, Merchant {
	private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.gnome.idle");
	private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.gnome.walk");
	private static final RawAnimation NONE = RawAnimation.begin().thenLoop("animation.gnome.none");
	private static final RawAnimation RESET = RawAnimation.begin().thenPlay("animation.gnome.reset");
	private static final RawAnimation ATTACK = RawAnimation.begin().thenPlay("animation.gnome.attack");
	private static final RawAnimation WORK = RawAnimation.begin().thenPlay("animation.gnome.work");
	private static final RawAnimation FISH = RawAnimation.begin().thenPlay("animation.gnome.fish");
	private static final RawAnimation TALK = RawAnimation.begin().thenPlay("animation.gnome.talk");
	private static final RawAnimation WAVE = RawAnimation.begin().thenPlay("animation.gnome.wave");
	private static final RawAnimation SIT = RawAnimation.begin().thenLoop("animation.gnome.sit");
	private static final RawAnimation SLEEP = RawAnimation.begin().thenLoop("animation.gnome.sleep");
	private static final RawAnimation PLAY_WHISTLE = RawAnimation.begin().thenLoop("animation.gnome.play_whistle");
	private static final RawAnimation PLAY_LUTE = RawAnimation.begin().thenLoop("animation.gnome.play_lute");
	private static final RawAnimation PLAY_BASS = RawAnimation.begin().thenLoop("animation.gnome.play_bass");
	private static final RawAnimation PLAY_DRUM = RawAnimation.begin().thenLoop("animation.gnome.play_drum");

	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

	// ---- opgeslagen staat ----
	private boolean initDone;
	private boolean nativeSpawn;
	private boolean anchor;
	private boolean hasHome;
	private BlockPos homePos;
	private boolean hasVillage;
	private BlockPos villageCenter;
	private UUID friend;
	private int friendBond;
	private int favorite;     // 0 muziek, 1 tuinieren, 2 boeken, 3 kletsen, 4 markt, 5 zitten
	private int instrument;   // 0 fluit, 1 luit, 2 bas, 3 trom
	private int tradeSeed;
	private int built;
	private int materials;
	private final UUID[] known = new UUID[4];

	// ---- tijdelijke staat ----
	private int villageTries;
	private int lastVoiceTick = -1000;
	private Player tradingPlayer;
	private MerchantOffers offers;
	private String actionAnim;
	private int actionPeriod;
	private int dangerUntil;
	private GnomeEntity chatInviter;
	private int chatInviteUntil;

	public GnomeEntity(EntityType<? extends GnomeEntity> type, Level level) {
		super(type, level);
		this.setPersistenceRequired();
		if (this.getNavigation() instanceof GroundPathNavigation ground) {
			ground.setCanOpenDoors(true);
		}
	}

	public static AttributeSupplier.Builder createGnomeAttributes(Profession p) {
		boolean warrior = p == Profession.WARRIOR;
		return Mob.createMobAttributes()
				.add(Attributes.MAX_HEALTH, warrior ? 30.0 : 16.0)
				.add(Attributes.MOVEMENT_SPEED, 0.27)
				.add(Attributes.ATTACK_DAMAGE, warrior ? 5.0 : 1.0)
				.add(Attributes.FOLLOW_RANGE, 24.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, warrior ? 0.3 : 0.0);
	}

	public Profession profession() {
		return Profession.fromType(this.getType());
	}

	@Override
	protected void registerGoals() {
		Profession p = Profession.fromType(this.getType());
		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.goalSelector.addGoal(0, new OpenDoorGoal(this, true));
		this.targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());

		if (p.isGuard()) {
			this.goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.15, true));
			this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Monster.class, true));
		} else {
			this.goalSelector.addGoal(1, new PanicGoal(this, 1.4));
			this.goalSelector.addGoal(1, new SeekSafetyGoal(this));
		}
		if (p == Profession.HEALER) this.goalSelector.addGoal(2, new HealerRoundsGoal(this));
		this.goalSelector.addGoal(2, new GatherGoal(this));
		this.goalSelector.addGoal(2, new HomeStayGoal(this));

		switch (p) {
			case FISHERMAN -> this.goalSelector.addGoal(3, new FishGoal(this));
			case HEALER -> this.goalSelector.addGoal(3, new HealerBrewGoal(this));
			case FARMER -> this.goalSelector.addGoal(3, new FarmGoal(this));
			case BUILDER -> {
				this.goalSelector.addGoal(3, new CollectMaterialsGoal(this));
				this.goalSelector.addGoal(3, new BuildGoal(this));
			}
			case WARRIOR, NITWIT -> { }
		}
		if (p.isGuard()) this.goalSelector.addGoal(4, new GuardPatrolGoal(this));

		this.goalSelector.addGoal(5, new MusicGoal(this));
		this.goalSelector.addGoal(5, new ChatGoal(this));
		this.goalSelector.addGoal(5, new SitGoal(this));
		this.goalSelector.addGoal(5, new VisitGoal(this));
		this.goalSelector.addGoal(5, new CuriousPlayerGoal(this));
		this.goalSelector.addGoal(6, new StayNearVillageGoal(this));
		this.goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 0.55));
		this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 6.0F));
		this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
	}

	// ====================================================================== tick
	@Override
	public void tick() {
		super.tick();
		if (this.level() instanceof ServerLevel server && !this.isRemoved()) {
			if (!this.initDone) this.initServer();
			if (this.isRemoved()) return;
			if (!this.hasVillage && (this.tickCount + this.getId()) % 40 == 0) this.findVillage(server);
		}
	}

	private void initServer() {
		if (this.nativeSpawn) {
			this.nativeSpawn = false;
			if (!this.anchor && this.random.nextDouble() >= GnomeConfig.get().populationFactor) {
				this.discard();
				return;
			}
		}
		this.initDone = true;
		this.favorite = this.random.nextInt(6);
		this.instrument = this.random.nextInt(4);
		this.tradeSeed = this.random.nextInt();
		if (!this.hasHome) {
			this.homePos = this.blockPosition();
			this.hasHome = true;
		}
		if (this.anchor && !this.hasVillage) {
			this.villageCenter = this.blockPosition();
			this.hasVillage = true;
		}
	}

	/** Het dorpscentrum is de plek van de 'anker'-gnomes op het plein; andere gnomes zoeken die op. */
	private void findVillage(ServerLevel server) {
		List<GnomeEntity> anchors = server.getEntitiesOfClass(GnomeEntity.class, this.getBoundingBox().inflate(70.0, 30.0, 70.0),
				g -> g != this && g.anchor && g.hasVillage);
		GnomeEntity best = null;
		double bestD = Double.MAX_VALUE;
		for (GnomeEntity g : anchors) {
			double d = this.distanceToSqr(g);
			if (d < bestD) {
				bestD = d;
				best = g;
			}
		}
		if (best != null) {
			this.villageCenter = best.villageCenter;
			this.hasVillage = true;
		} else if (++this.villageTries >= 8 && this.hasHome) {
			this.villageCenter = this.homePos;
			this.hasVillage = true;
		}
	}

	@Override
	public void aiStep() {
		super.aiStep();
		if (this.level().isClientSide() || !(this.level() instanceof ServerLevel server) || !this.isAlive()) return;

		// Tijdens het handelen blijft de gnome staan en kijkt naar de speler.
		if (this.tradingPlayer != null) {
			if (!this.tradingPlayer.isAlive() || this.distanceToSqr(this.tradingPlayer) > 100.0) {
				this.tradingPlayer = null;
			} else {
				this.getNavigation().stop();
				this.getLookControl().setLookAt(this.tradingPlayer);
			}
		}
		if (this.tradingPlayer == null && this.tickCount % 24000 == 23999) this.offers = null;

		// Werk-animatie herhalen zolang de gnome aan het werk is.
		if (this.actionAnim != null && this.actionPeriod > 0 && this.tickCount % this.actionPeriod == 0) {
			this.triggerAnim("action", this.actionAnim);
		}

		// Healer: geneest gewonden in de buurt (spelers, gnomes, golems, dorpelingen).
		if (this.profession() == Profession.HEALER && this.tickCount % 40 == 0) {
			List<LivingEntity> hurt = server.getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(6.0),
					e -> e != this && e.isAlive() && e.getHealth() < e.getMaxHealth() - 2.0F
							&& (e instanceof Player || e instanceof GnomeEntity || GnomeUtil.isFriendlyType(e)));
			if (!hurt.isEmpty()) this.castHeal(server, hurt.get(0));
		}

		// Wachters: komen anderen te hulp en blijven bij het dorp.
		if (this.profession().isGuard() && (this.tickCount + this.getId()) % 20 == 0) {
			if (this.getTarget() == null) {
				List<GnomeEntity> hurtAllies = server.getEntitiesOfClass(GnomeEntity.class, this.getBoundingBox().inflate(24.0, 8.0, 24.0),
						g -> g != this && g.getLastHurtByMob() instanceof Monster m && m.isAlive());
				if (!hurtAllies.isEmpty() && hurtAllies.get(0).getLastHurtByMob() != null) this.setTarget(hurtAllies.get(0).getLastHurtByMob());
			} else if (this.hasVillage) {
				double lim = GnomeConfig.get().villageRadius + 10.0;
				if (this.getTarget().distanceToSqr(this.villageCenter.getX() + 0.5, this.villageCenter.getY(), this.villageCenter.getZ() + 0.5) > lim * lim) {
					this.setTarget(null);
				}
			}
		}

		// Noodgreep: te ver van het dorp of vast? Dan terug naar huis (alleen als niemand het ziet).
		if (this.hasVillage && this.hasHome && (this.tickCount + this.getId()) % 200 == 0) {
			double lim = GnomeConfig.get().villageRadius + 16.0;
			if (this.distanceToSqr(this.villageCenter.getX() + 0.5, this.villageCenter.getY(), this.villageCenter.getZ() + 0.5) > lim * lim
					&& server.getNearestPlayer(this, 24.0) == null) {
				this.getNavigation().stop();
				this.setPos(this.homePos.getX() + 0.5, this.homePos.getY(), this.homePos.getZ() + 0.5);
			}
		}
	}

	public void castHeal(ServerLevel server, LivingEntity patient) {
		patient.heal(5.0F);
		server.sendParticles(ParticleTypes.HEART, patient.getX(), patient.getY() + patient.getBbHeight() + 0.2, patient.getZ(), 5, 0.3, 0.2, 0.3, 0.0);
		server.playSound(null, patient.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.NEUTRAL, 1.0F, 1.4F);
		this.triggerAnim("action", "work");
		this.voice(ModSounds.HEAL, 1.0F);
	}

	@Override
	public void swing(InteractionHand hand) {
		if (!this.level().isClientSide()) {
			this.triggerAnim("action", "attack");
			if (this.profession().isGuard() && this.random.nextInt(3) == 0) this.voice(ModSounds.ATTACK, 1.0F);
		}
		super.swing(hand);
	}

	// ====================================================================== dagritme
	public DayTracker.Phase phase() {
		if (this.level() instanceof ServerLevel server) return DayTracker.phase(server);
		return DayTracker.Phase.WORK;
	}

	public boolean shouldShelter() {
		if (!GnomeConfig.get().shelterInStorms) return false;
		Level l = this.level();
		return l.isThundering() || (l.isRaining() && this.getId() % 3 != 0 && !this.profession().isGuard());
	}

	public boolean isWorkTime() {
		return this.phase() == DayTracker.Phase.WORK && !this.shouldShelter();
	}

	public boolean isNight() {
		return this.phase() == DayTracker.Phase.NIGHT;
	}

	/** Is er vanavond een gemeenschappelijke gebeurtenis die deze gnome bijwoont? */
	public boolean attendsEvent() {
		if (!GnomeConfig.get().communalEvents || this.profession().isGuard() || !this.hasVillage || this.shouldShelter()) return false;
		if (!(this.level() instanceof ServerLevel server)) return false;
		return DayTracker.phase(server) == DayTracker.Phase.EVENING
				&& DayTracker.eventOfTonight(server, this.villageCenter.asLong()) > 0;
	}

	public int tonightsEvent() {
		if (!(this.level() instanceof ServerLevel server) || !this.hasVillage) return 0;
		return DayTracker.eventOfTonight(server, this.villageCenter.asLong());
	}

	/** Vrije tijd: geen gevaar, niet aan het handelen. Beroepsmensen hebben overdag minder vrije tijd. */
	public boolean canLeisure() {
		if (this.getTarget() != null || this.tradingPlayer != null || this.inDanger() || this.shouldShelter()) return false;
		DayTracker.Phase ph = this.phase();
		if (ph == DayTracker.Phase.NIGHT) return false;
		if (ph == DayTracker.Phase.EVENING && this.attendsEvent()) return false;
		return true;
	}

	public boolean busyLeisureChance() {
		if (this.profession() == Profession.NITWIT) return true;
		return this.phase() != DayTracker.Phase.WORK || this.random.nextInt(4) == 0;
	}

	// ====================================================================== gevaar
	public boolean inDanger() {
		return this.tickCount < this.dangerUntil;
	}

	public void markDanger(int ticks) {
		this.dangerUntil = Math.max(this.dangerUntil, this.tickCount + ticks);
	}

	// ====================================================================== getters voor goals
	public boolean hasHome() { return this.hasHome; }
	public BlockPos home() { return this.homePos; }
	public BlockPos homePos() { return this.homePos; }
	public boolean hasVillage() { return this.hasVillage; }
	public BlockPos villageCenter() { return this.villageCenter; }
	public boolean isAnchor() { return this.anchor; }
	public int favorite() { return this.favorite; }
	public int instrument() { return this.instrument; }
	public int builtCount() { return this.built; }
	public void addBuilt() { this.built++; }
	public int materials() { return this.materials; }
	public void addMaterials(int n) { this.materials = Math.max(0, this.materials + n); }
	public UUID friend() { return this.friend; }
	public int friendBond() { return this.friendBond; }

	public double distanceToVillageSqr() {
		if (!this.hasVillage) return 0.0;
		return this.distanceToSqr(this.villageCenter.getX() + 0.5, this.villageCenter.getY(), this.villageCenter.getZ() + 0.5);
	}

	public boolean playsMusic() {
		return GnomeConfig.get().musicEnabled && (this.profession() == Profession.NITWIT || this.favorite == 0);
	}

	/** Vriendschap: na een paar gezellige gesprekken worden twee vriendeloze gnomes vrienden. */
	public void chattedWith(GnomeEntity other) {
		if (!GnomeConfig.get().friendships) return;
		if (other.getUUID().equals(this.friend)) {
			this.friendBond = Math.min(10, this.friendBond + 1);
			return;
		}
		if (this.friend == null && other.friend == null) {
			this.friendBond++;
			other.friendBond++;
			if (this.friendBond >= 3 && other.friendBond >= 3) {
				this.friend = other.getUUID();
				other.friend = this.getUUID();
			}
		}
	}

	public void makeFriendsWith(GnomeEntity other) {
		if (GnomeConfig.get().friendships && this.friend == null && other.friend == null) {
			this.friend = other.getUUID();
			other.friend = this.getUUID();
			this.friendBond = Math.max(this.friendBond, 3);
			other.friendBond = Math.max(other.friendBond, 3);
		}
	}

	public boolean knows(UUID player) {
		for (UUID u : this.known) if (player.equals(u)) return true;
		return false;
	}

	public void learn(UUID player) {
		if (this.knows(player)) return;
		for (int i = this.known.length - 1; i > 0; i--) this.known[i] = this.known[i - 1];
		this.known[0] = player;
	}

	public void inviteToChat(GnomeEntity inviter, int ticks) {
		this.chatInviter = inviter;
		this.chatInviteUntil = this.tickCount + ticks;
	}

	public GnomeEntity chatInviter() {
		return (this.chatInviter != null && this.chatInviter.isAlive() && this.tickCount < this.chatInviteUntil) ? this.chatInviter : null;
	}

	public void clearInvite() {
		this.chatInviter = null;
	}

	// ====================================================================== animaties
	public void startAnim(String name) {
		if (this.level().isClientSide()) return;
		if (name.equals(this.actionAnim)) return;
		this.actionAnim = name;
		this.actionPeriod = switch (name) {
			case "fish" -> 60;
			case "work" -> 18;
			case "talk" -> 30;
			default -> 0;   // lussen (zitten, slapen, spelen) en eenmalige animaties
		};
		this.triggerAnim("action", name);
	}

	public void stopAnim() {
		if (this.level().isClientSide() || this.actionAnim == null) return;
		this.actionAnim = null;
		this.triggerAnim("action", "reset");
	}

	public void oneShot(String name) {
		if (!this.level().isClientSide()) this.triggerAnim("action", name);
	}

	public String instrumentAnim(int part) {
		return switch (part) {
			case 0 -> "play_whistle";
			case 1 -> "play_lute";
			case 2 -> "play_bass";
			default -> "play_drum";
		};
	}

	// ====================================================================== opslaan
	private static void putUuid(ValueOutput out, String key, UUID u) {
		long m = u.getMostSignificantBits();
		long l = u.getLeastSignificantBits();
		out.putInt(key + "0", (int) (m >>> 32));
		out.putInt(key + "1", (int) m);
		out.putInt(key + "2", (int) (l >>> 32));
		out.putInt(key + "3", (int) l);
	}

	private static UUID getUuid(ValueInput in, String key) {
		int a = in.getIntOr(key + "0", 0);
		int b = in.getIntOr(key + "1", 0);
		int c = in.getIntOr(key + "2", 0);
		int d = in.getIntOr(key + "3", 0);
		if ((a | b | c | d) == 0) return null;
		return new UUID(((long) a << 32) | (b & 0xFFFFFFFFL), ((long) c << 32) | (d & 0xFFFFFFFFL));
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput output) {
		super.addAdditionalSaveData(output);
		output.putInt("Init", this.initDone ? 1 : 0);
		output.putInt("Native", this.nativeSpawn ? 1 : 0);
		output.putInt("Anchor", this.anchor ? 1 : 0);
		output.putInt("Built", this.built);
		output.putInt("Mats", this.materials);
		output.putInt("Fav", this.favorite);
		output.putInt("Inst", this.instrument);
		output.putInt("TradeSeed", this.tradeSeed);
		output.putInt("Bond", this.friendBond);
		output.putInt("HasHome", this.hasHome ? 1 : 0);
		if (this.hasHome) {
			output.putInt("HomeX", this.homePos.getX());
			output.putInt("HomeY", this.homePos.getY());
			output.putInt("HomeZ", this.homePos.getZ());
		}
		output.putInt("HasVill", this.hasVillage ? 1 : 0);
		if (this.hasVillage) {
			output.putInt("VillX", this.villageCenter.getX());
			output.putInt("VillY", this.villageCenter.getY());
			output.putInt("VillZ", this.villageCenter.getZ());
		}
		if (this.friend != null) putUuid(output, "Fr", this.friend);
		for (int i = 0; i < this.known.length; i++) {
			if (this.known[i] != null) putUuid(output, "K" + i + "_", this.known[i]);
		}
	}

	@Override
	protected void readAdditionalSaveData(ValueInput input) {
		super.readAdditionalSaveData(input);
		this.initDone = input.getIntOr("Init", 0) == 1;
		this.nativeSpawn = input.getIntOr("Native", 0) == 1;
		this.anchor = input.getIntOr("Anchor", 0) == 1;
		this.built = input.getIntOr("Built", 0);
		this.materials = input.getIntOr("Mats", 0);
		this.favorite = input.getIntOr("Fav", 0);
		this.instrument = input.getIntOr("Inst", 0);
		this.tradeSeed = input.getIntOr("TradeSeed", 0);
		this.friendBond = input.getIntOr("Bond", 0);
		this.hasHome = input.getIntOr("HasHome", 0) == 1;
		if (this.hasHome) this.homePos = new BlockPos(input.getIntOr("HomeX", 0), input.getIntOr("HomeY", 0), input.getIntOr("HomeZ", 0));
		this.hasVillage = input.getIntOr("HasVill", 0) == 1;
		if (this.hasVillage) this.villageCenter = new BlockPos(input.getIntOr("VillX", 0), input.getIntOr("VillY", 0), input.getIntOr("VillZ", 0));
		this.friend = getUuid(input, "Fr");
		for (int i = 0; i < this.known.length; i++) this.known[i] = getUuid(input, "K" + i + "_");
	}

	@Override
	public boolean removeWhenFarAway(double distanceToClosestPlayer) {
		return false;
	}

	// ====================================================================== geluiden
	private float voicePitch() {
		return switch (this.profession()) {
			case WARRIOR -> 0.9F;
			case BUILDER -> 0.85F;
			case FISHERMAN -> 0.95F;
			case FARMER -> 1.0F;
			case HEALER -> 1.1F;
			case NITWIT -> 1.2F;
		};
	}

	/** Stemgeluid met lichte variatie; niet-belangrijke geluiden zijn begrensd zodat het dorp niet constant kwetter. */
	public void voice(SoundEvent sound, float volume) {
		if (sound == null || this.level().isClientSide()) return;
		boolean important = sound == ModSounds.ATTACK || sound == ModSounds.ALERT || sound == ModSounds.YES
				|| sound == ModSounds.NO || sound == ModSounds.HEAL || sound == ModSounds.GREET;
		if (!important && this.tickCount - this.lastVoiceTick < 300) return;
		this.lastVoiceTick = this.tickCount;
		this.playSound(sound, volume, this.voicePitch() + (this.random.nextFloat() - 0.5F) * 0.12F);
	}

	@Override
	protected SoundEvent getAmbientSound() {
		if (this.isNight() && this.hasHome
				&& this.distanceToSqr(this.homePos.getX() + 0.5, this.homePos.getY(), this.homePos.getZ() + 0.5) < 36.0) {
			return ModSounds.SNORE;
		}
		if (this.level().getNearestPlayer(this, 12.0) == null) return null;
		return ModSounds.AMBIENT;
	}

	@Override
	public int getAmbientSoundInterval() {
		return GnomeConfig.get().ambientSoundIntervalTicks;
	}

	@Override
	protected SoundEvent getHurtSound(DamageSource source) {
		return ModSounds.HURT;
	}

	@Override
	protected SoundEvent getDeathSound() {
		return ModSounds.DEATH;
	}

	@Override
	protected void playStepSound(BlockPos pos, BlockState state) {
		if (this.random.nextInt(2) == 0) this.playSound(ModSounds.STEP, 0.2F, 0.9F + this.random.nextFloat() * 0.3F);
	}

	@Override
	public void setTarget(LivingEntity target) {
		boolean newTarget = target != null && this.getTarget() == null;
		super.setTarget(target);
		if (newTarget && this.profession().isGuard()) this.voice(ModSounds.ATTACK, 1.0F);
	}

	// ====================================================================== interactie en handel
	@Override
	public InteractionResult mobInteract(Player player, InteractionHand hand) {
		if (!this.level().isClientSide() && this.isAlive()) {
			this.getLookControl().setLookAt(player);
			if (!this.profession().canTrade()) {
				// Nitwits handelen niet: ze kletsen alleen wat.
				this.oneShot("talk");
				this.voice(ModSounds.LAUGH, 1.0F);
			} else if (this.tradingPlayer == null) {
				this.tradingPlayer = player;
				this.voice(ModSounds.YES, 1.0F);
				this.openTradingScreen(player, this.getDisplayName(), 1);
			}
		}
		return InteractionResult.SUCCESS;
	}

	public boolean isTrading() {
		return this.tradingPlayer != null;
	}

	public void setTradingPlayer(Player player) {
		this.tradingPlayer = player;
	}

	public Player getTradingPlayer() {
		return this.tradingPlayer;
	}

	public MerchantOffers getOffers() {
		if (this.offers == null) {
			this.offers = new MerchantOffers();
			GnomeTrades.fill(this.offers, this.profession(), this.tradeSeed);
		}
		return this.offers;
	}

	public void overrideOffers(MerchantOffers newOffers) {
		this.offers = newOffers;
	}

	public void notifyTrade(MerchantOffer offer) {
		offer.increaseUses();
		this.voice(ModSounds.CELEBRATE, 1.0F);
	}

	public void notifyTradeUpdated(ItemStack stack) {
	}

	public int getVillagerXp() {
		return 0;
	}

	public void overrideXp(int xp) {
	}

	public boolean showProgressBar() {
		return false;
	}

	public SoundEvent getNotifyTradeSound() {
		return ModSounds.YES;
	}

	public boolean isClientSide() {
		return this.level().isClientSide();
	}

	public boolean stillValid(Player player) {
		return this.tradingPlayer == player && this.isAlive() && this.distanceToSqr(player) <= 64.0;
	}

	// ====================================================================== GeckoLib
	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(new AnimationController<GnomeEntity>("move", 4,
				state -> state.isMoving() ? state.setAndContinue(WALK) : state.setAndContinue(IDLE)));
		controllers.add(new AnimationController<GnomeEntity>("action", 3, state -> state.setAndContinue(NONE))
				.triggerableAnim("reset", RESET)
				.triggerableAnim("attack", ATTACK)
				.triggerableAnim("work", WORK)
				.triggerableAnim("fish", FISH)
				.triggerableAnim("talk", TALK)
				.triggerableAnim("wave", WAVE)
				.triggerableAnim("sit", SIT)
				.triggerableAnim("sleep", SLEEP)
				.triggerableAnim("play_whistle", PLAY_WHISTLE)
				.triggerableAnim("play_lute", PLAY_LUTE)
				.triggerableAnim("play_bass", PLAY_BASS)
				.triggerableAnim("play_drum", PLAY_DRUM));
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return this.cache;
	}
}

from pomp.example_problems.gripper import *

states = [[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3141592653589793, 0.3141592653589793, 0.3141592653589793, 0.3141592653589793, 0.3141592653589793, 0.3141592653589793, 0.3141592653589793, 0.3141592653589793, 0.3141592653589793], [0.0023014463274898334, 0.8088874280176308, 0.0039830505714045965, -6.599226002560897e-08, 8.615764381137037e-08, -0.0010024612992070008, -5.416173681009032e-07, -4.1875920118557675e-07, 1.197290966249015e-07, 1.3906337011193838e-06, -1.7942605132037556e-06, -8.125118916326255e-09, -1.7309452001468006e-05, 0.6500000000000006, 0.41286437692466804, 5.517489636173484e-06, 0.6500000000000006, 0.28798059282544425, -3.745992894005622e-05, 0.6500000000000002, 0.06203985962351103], [0.11376221482906347, 1.0505064956244061, 0.0005580878201614848, -0.012659417534478131, 0.06303914343929475, -0.006249448523868703, 0.10722369435321775, -0.05030736804417206, 0.25327819359364917, -0.14260763872488344, 1.1428725087606217, -0.11013178510257592, 7.3525624853061184e-06, 0.6500000000000002, 0.6505673203722444, -1.7364170573113168e-05, 0.6500000000000002, 0.46118080408487305, -2.096719478326968e-06, 0.602843308396695, 0.6430485630669234], [-0.21229904964210022, 0.9273634030656279, -0.04657905147898951, -0.043894950979306666, 1.0246384397617216, -0.10353896093990976, -0.7642003811689909, -0.06633025646575942, -0.3172764552462528, 0.86743857930153, 0.7643228020640069, -0.3597013920193624, 1.3070399953902171e-05, 0.6500000000000002, 0.650540087699841, 1.638757496771527e-05, 0.6500000000000002, 0.40693699909799824, 2.5459349984197874e-05, 0.6500000000000002, 0.41254667662636796], [-0.0049221029233019395, 1.2868495238634223, 0.01728213431695162, 0.275598945226858, 0.6296078737351294, 0.4146795998194033, 0.6456562102765003, 0.17319185227928438, 1.0689324857615932, 0.8591441868314911, -1.661405050976692, 0.13158319658738807, -4.3187560970766806e-07, 0.650000010869383, 0.615033252420322, -9.447649136250984e-07, 0.6500000000761076, 0.4439696593610499, -0.00024457592069070507, 0.6500274568422086, 0.6471214224278233], [0.1143524861286767, 1.0306639547915015, 0.08874379371184132, 0.47822987984399645, -0.015799846964305028, -0.5800942110112249, -0.013078812514859173, 0.16964922892409398, -1.6056522407668201, 0.44590711158317653, -0.09259725191608413, -0.5646628017693751, -2.229500185782118e-05, 0.6500000000000002, 0.6505618960582592, -1.5783671793673297e-05, 0.6500000000000002, 0.41060800204102976, -0.00027343810101965817, 0.6500390315250093, 0.6487004212340273], [0.3361136703911566, 0.8108445946601956, 0.4690867767427548, -0.03336128140962378, -0.012399212612792062, -0.67360687992314, 0.37021509519019374, 0.37069319923246385, -0.028947315756360316, 0.42032571824191023, -0.004120340282101765, -0.38525989463047744, -2.505310277340617e-06, 0.6500000000000002, 0.6505562095110282, 8.179320397376244e-06, 0.6500000000000002, 0.4371192970267405, -0.0003847169376066272, 0.6500313665189447, 0.6500666889837594], [1.0504955617442369, 0.6747218363209125, 0.7600777043642428, -0.22876516640189262, -0.06679552614437798, -1.1470163378754754, 1.2874376662378306, 0.31496595777937664, -0.459672922111666, -0.3201362885931574, 0.27300598481776606, -0.5597186808166821, -2.505303201636904e-06, 0.6500000000000002, 0.6505562093813197, -9.461831971998797e-07, 0.6500000000000002, 0.4242766261778808, -0.0002447279205774965, 0.6500331662154427, 0.6500483907053686], [1.8259872377578015, 0.11536294538652293, 0.9869101484420655, -0.47764027929102104, -0.24588096547691485, -1.5181488045395402, 0.8008333394563723, 0.29376418871213317, -1.0306638631724256, -0.3044574426734327, 0.25963537072734, -0.5323061591263691, -1.4388195315546558e-05, 0.6500000000000002, 0.6505867961019483, 8.178354757176332e-06, 0.6500000000000002, 0.4274248199264244, -0.0002447279205774961, 0.6500331662154427, 0.6500483907053686], [2.837821455274444, -1.4568064911741294, 1.2336315216233469, -0.6743060389172292, -0.5340732248361053, -1.9035506023103295, 1.4643188012550996, 0.2630011335301829, -2.47925595544027, -0.2872439016485035, 0.24495599857504968, -0.502210412977136, -2.2294971351741893e-05, 0.6500000000000002, 0.6505618957549183, -1.5782808883714728e-05, 0.6500000000000002, 0.4289366301908834, -0.0002447279205774964, 0.6500331662154427, 0.6500483907053686]]
inputs= [[0.8757821883223107, -0.0386751682246218, 0.0, 7.256368520707356, 0.0, 0.0, 0.0], [0.7604300505262902, 0.42926675858359586, 0.0, 10.739720096491384, 0.0, 0.0, 0.0], [0.9124114341389773, -1.0571034406878406, 0.0, 8.859254914786199, 0.0, 0.0, 0.0], [0.7351299279240561, 0.638775550643238, 0.0, 12.748068443609661, 0.0, 0.0, 0.0], [0.9660888607800006, 0.6908007755990764, 0.0, 6.926079129608265, 0.0, 0.0, 0.0], [0.9859609356500025, 0.8912703940691009, 0.0, 7.732647140234305, 0.0, 0.0, 0.0], [0.8782345061178509, 1.192570338424272, 0.0, 8.95598363402827, 0.0, 0.0, 0.0], [0.7481177992813012, -0.5549376073915722, 0.0, 8.974788125111143, 0.0, 0.0, 0.0], [0.8834632143341669, 0.8975870083524788, 0.0, 7.9405716810874285, 0.0, 0.0, 0.0]]

movable_joints = [1,2,3,5,6,7,9,10,11]
num_joints = len(movable_joints)
num_dim_se3 = 6
data = [0.0, 1., 0.0, 0.0, 0.0, 0.0] + [0.0,]*num_dim_se3 + [math.pi/10]*num_joints + [0.0]*num_joints
gripper_vel = data[-num_joints:]
dynamics_sim = forwardSimulationGripper(gui=1)

cage = Gripper(data, dynamics_sim, movable_joints)
cage.controlSpace()
time.sleep(4.5)

new_states = states[0]
for i in range(len(inputs)):
    dynamics_sim.reset_states(states[i]+gripper_vel)
    new_states, viapoints = dynamics_sim.run_forward_sim(inputs[i])
    print('new_states', new_states)

dynamics_sim.finish_sim()

from SlotMachine import SlotMachine

slot = SlotMachine(
        num_reels=3,
        reel_array=['/test/club.png', '/test/club.png', '/test/club.png',
                    '/test/diamond.png', '/test/diamond.png', '/test/diamond.png',
                    '/test/heart.png', '/test/heart.png', '/test/heart.png',
                    '/test/spade.png', '/test/spade.png', '/test/spade.png',
                    '/test/diamond-gem.png'],
        award_dict={'/test/club.png':1,'/test/diamond.png':1,'/test/heart.png':1,'/test/spade.png':1,'/test/diamond-gem.png':1000}
,
        window=3,
        center_only=False
    )

slot.visualize()
print(slot.windowToJson())